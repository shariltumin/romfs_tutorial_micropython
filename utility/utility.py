import sys
import esp32
import gc
import os
import machine as mc
from platform import platform
import binascii

try:
    arch = sys.platform
    print("arch: ", arch)
except:
    print('arch: unknown')

def free_heap():
    return sum(r[1] for r in esp32.idf_heap_info(esp32.HEAP_DATA))

def heap_frag():
    """Return fragmentation ratio (0.0 = none, 1.0 = fully fragmented)."""
    info = esp32.idf_heap_info(esp32.HEAP_DATA)
    total_free = sum(r[1] for r in info)
    largest = sum(r[2] for r in info)
    return 1 - (largest / total_free) if total_free else 0

def what_dir(w):
    """Uses dir() to safely inspect any object, including built-ins."""
    # dir(w) gives us the text names of all attributes
    for k in dir(w):
        try:
            # Fetch the actual value safely using the text name
            v = getattr(w, k)
            print(f'| {k:20} | {v!s:20} |')
        except AttributeError:
            # Some virtual hardware properties can't be read directly
            print(f'| {k:20} | <Unreadable property> |')

def what(w):
    for k, v in w.__dict__.items():
        # Notice the !s before the :20
        # This will cast v to string, i.e. {str(v):20}
        print(f'| {k:20} | {v!s:20} |')

def sysinfo():
    uname = os.uname()
    mem_total = gc.mem_alloc()+gc.mem_free()
    free_percent = "("+str((gc.mem_free())/mem_total*100.0)+"%)"
    alloc_percent = "("+str((gc.mem_alloc())/mem_total*100.0)+"%)"
    stat = os.statvfs('/flash')
    block_size = stat[0]
    total_blocks = stat[2]
    free_blocks  = stat[3]
    rom_total = (total_blocks * block_size)/1024
    rom_free = (free_blocks * block_size)/1024
    rom_usage = (rom_total-rom_free)
    rfree_percent = "("+str(rom_free/rom_total*100.0)+"%)"
    rusage_percent = "("+str(rom_usage/rom_total*100.0)+"%)"
    ID = binascii.hexlify(mc.unique_id())
    print("ID ............: ", end="")
    print(ID.decode())

    print("MCU ...........:",sys.implementation[2].split()[0])
    print("Memory")
    print("   total ......:",mem_total/1024,"KB")
    print("   usage ......:",gc.mem_alloc()/1024,"KB",alloc_percent)
    print("   free .......:",gc.mem_free()/1024,"KB",free_percent)
    print("Filesystem")
    print("   total ......:", rom_total,"KB" )
    print("   usage ......:", rom_usage,"KB",rusage_percent )
    print("   free .......:", rom_free,"KB",rfree_percent )
    print("SYSTEM")
    print("   platform ...:",platform())
    print("   type .......:",sys.implementation[2].split()[-1])
    print("   node .......:",uname.nodename)
    print("   release ....:",uname.release)
    print("   version ....:",uname.version)
    print("   board ......:",uname.machine)
    try:
       print("   speed ......:",mc.freq(), 'Hz')
    except:
       pass # nrf


