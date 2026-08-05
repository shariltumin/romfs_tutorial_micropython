
For anyone else (or my future self) setting up a dedicated 1 MB ROMFS partition on an ESP32 MicroPython target with 4 MB Flash, here is the full required configuration stack:

1. **Partition Table (`partitions.csv`):**
```csv
# This partition table is for devices with 4MiB
# The first 2MiB is used for bootloader, nvs, phy_init and firmware.
# Next 1MiB is for ROMFS. Last 1MiB is for VFS
# Name,   Type, SubType, Offset,   Size,     Flags
nvs,      data, nvs,     0x9000,   0x6000,
phy_init, data, phy,     0xf000,   0x1000,
factory,  app,  factory, 0x10000,  0x1F0000,
romfs,    data, 0x81,    0x200000, 0x100000,
vfs,      data, spiffs,  0x300000, 0x100000,
```
---

2. **C Configuration (`mpconfigport.h` or `mpconfigboard.h`):**
```c
#define MICROPY_VFS_ROM                   (1)
#define MICROPY_VFS_ROM_IOCTL             (1)

```
---

3. **Host Tools:**
```bash
pip install mpremote mpy-cross

```
We need to pip install mpy-cross even if we alrealy have `mpy-cross` in our $PATH. When mpremote runs, it executes `import mpy_cross` inside Python, so it had to be a Python package.

---

4. **Deploy Command:**
```bash
$ mpremote a0 romfs deploy utility
Building romfs filesystem, source directory: utility/
/
\-- utility.py -> .mpy
Image size is 1544 bytes
ROMFS0 partition has size 1048576 bytes (256 blocks of 4096 bytes each)
Preparing ROMFS0 partition for writing
Writing at offset 0
ROMFS image deployed
```

The new deployment will override the previous one in the ROMFS. We can only have one deployment, this time the image takes 1544 bytes, the rest of the space is wasted.

---

5. **Query Command:**
```bash
$ mpremote a0 romfs query
ROMFS0 partition has size 1048576 bytes (256 blocks of 4096 bytes each)
  Raw contents: d2:cd:31:8c:03:05:8c:00:0b:75:74:69 ...
  ROMFS image size: 1539
```
---

6. **Import ROMFS library**
```bash
>>> import utility as u
arch:  esp32
>>> u.free_heap()
165792
>>> u.heap_frag()
0.03956765
>>> u.what_dir(u)
| __class__            | <class 'module'>     |
| __name__             | utility              |
| __dict__             | {'sys': <module 'sys'>, 'esp32': <module 'esp32'>, '__name__': 'utility', 'free_heap': <function free_heap at 0x3fca9c50>, 'heap_frag': <function heap_frag at 0x3fca9df0>, 'what_dir': <function what_dir at 0x3fca9e00>, '__file__': '/rom/utility.mpy', 'arch': 'esp32', 'what': <function what at 0x3fca9e10>} |
| __file__             | /rom/utility.mpy     |
| esp32                | <module 'esp32'>     |
| sys                  | <module 'sys'>       |
| free_heap            | <function free_heap at 0x3fca9c50> |
| heap_frag            | <function heap_frag at 0x3fca9df0> |
| what_dir             | <function what_dir at 0x3fca9e00> |
| what                 | <function what at 0x3fca9e10> |
| arch                 | esp32                |
>>> u.what(u)
| sys                  | <module 'sys'>       |
| esp32                | <module 'esp32'>     |
| __name__             | utility              |
| free_heap            | <function free_heap at 0x3fca9c50> |
| heap_frag            | <function heap_frag at 0x3fca9df0> |
| what_dir             | <function what_dir at 0x3fca9e00> |
| __file__             | /rom/utility.mpy     |
| arch                 | esp32                |
| what                 | <function what at 0x3fca9e10> |
>>> u.sysinfo()
ID ............: 8856a6eb58d0
MCU ...........: ESP32-C3
Memory
   total ......: 174.0 KB
   usage ......: 5.328125 KB (2.6041664%)
   free .......: 168.656252 KB (97.467672%)
Filesystem
   total ......: 1024.0 KB
   usage ......: 12.0 KB (1.171875%)
   free .......: 1012.0 KB (98.828132%)
SYSTEM
   platform ...: MicroPython-1.28.0-riscv-IDFv5.5.5-dirty-with-newlib4.3.0
   type .......: ESP32-C3
   node .......: esp32
   release ....: 1.28.0
   version ....: v1.28.0-kaki5 on 2026-08-05
   board ......: ESP32-C3 BlueBoard USB-Repl (KAKI5) with ESP32-C3
   speed ......: 160000000 Hz
```
---

7. **Why ROMFS matters**

ROMFS (Read-Only File System) provides significant performance, security, and resource optimization advantages in microcontrollers and embedded systems like MicroPython.

While standard writable filesystems like FAT or LittleFS treat storage as dynamic drives, ROMFS treats fixed flash memory as an immutable, directly addressable extension of your code base.

### Key Technical Advantages

#### 1. In-Place Execution (XIP - Execute-in-Place)

* **Standard Filesystems (LittleFS/FAT):** When MicroPython imports a script or opens a file from a writable partition, it must copy data from SPI flash into internal RAM before executing or processing it.
* **ROMFS:** Data structures and pre-compiled `.mpy` bytecode reside in contiguous, read-only flash memory blocks. MicroPython can execute code directly out of flash (XIP) without taking up precious internal SRAM.

#### 2. Zero System Overhead & SRAM Conservation

Microcontrollers like the ESP32 often have restricted RAM allocations for heap usage.

* **No Dynamic Allocation:** ROMFS requires no dynamic RAM allocations for file allocation tables, directory trees, or write-buffering.
* **Predictable Memory Footprint:** Flash memory usage remains fixed at compile/flash time, eliminating out-of-memory errors caused by RAM fragmentation during file reads.

#### 3. Power-Failure Safety & System Integrity

Writable filesystems carry risks during unexpected power loss or brownout events:

* **Corruption Immunity:** Because ROMFS partition blocks are strictly read-only at runtime, a power outage during execution cannot corrupt system utilities, library files, or core configuration assets.
* **Fail-Safe Recovery:** Critical application recovery scripts or fallback logic placed in ROMFS remain intact even if the primary writable VFS partition gets corrupted by user scripts or power cuts.

#### 4. Instant Boot & Import Times

Traditional filesystem drivers parse file systems on-demand by reading directory headers, verifying block tables, and traversing tree structures. ROMFS uses a simple, flat binary header structure:

* Lookups require minimal CPU instructions.
* Module imports execute almost instantly compared to dynamic disk access.

### Architectural Comparison

| Metric / Feature | Dynamic VFS (LittleFS / FAT) | ROMFS (Read-Only Partition) |
| --- | --- | --- |
| **Primary Use Case** | User data, logs, dynamic settings | Core modules, system utilities, web assets |
| **RAM Consumption** | High (buffers, directory caching) | Zero / Minimal (Direct Flash XIP) |
| **Power Loss Risk** | Potential filesystem corruption | Immune to runtime corruption |
| **Write Wear** | Subjects flash blocks to write cycles | No runtime wear (written only at flash time) |
| **Access Speed** | Moderate (traversal overhead) | Fast (direct address offsets) |


### Practical Real-World Applications

* **Frozen Libraries / Embedded Utilities:** Distribute core drivers (e.g., WiFi handling, web servers, sensors) without taking up main application space or risking accidental deletion by users.
* **Fixed Web & GUI Assets:** Store static HTML, CSS, JavaScript, icons, or binary assets for embedded web servers (e.g., ESPAsyncWebServer) directly in flash memory.
* **Firmware Recovery:** Store a factory-reset script in `/rom` that can re-format and re-populate a corrupted main `/flash` partition.
