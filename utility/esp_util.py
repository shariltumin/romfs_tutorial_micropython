# esp_util.py
import esp32

def free_heap():
    return sum(r[1] for r in esp32.idf_heap_info(esp32.HEAP_DATA))

def heap_frag():
    """Return fragmentation ratio (0.0 = none, 1.0 = fully fragmented)."""
    info = esp32.idf_heap_info(esp32.HEAP_DATA)
    total_free = sum(r[1] for r in info)
    largest = sum(r[2] for r in info)
    return 1 - (largest / total_free) if total_free else 0

