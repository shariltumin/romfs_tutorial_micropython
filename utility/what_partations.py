import esp32, machine

# parts = esp32.Partition.find(type=esp32.Partition.TYPE_DATA)
for part in esp32.Partition.find(type=esp32.Partition.TYPE_DATA):
    print(part)
