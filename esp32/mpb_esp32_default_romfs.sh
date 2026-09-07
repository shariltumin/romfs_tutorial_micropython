#!/bin/bash

export PATH="$HOME/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

echo "=========================================================="
echo "Setting up for esp32 build"
echo "Using esp-idf-555"
export IDF_PATH="$HOME/disk/esp/esp-idf-555"
echo "MCU type esp32"
export IDF_TARGET="esp32"
source $IDF_PATH/export.sh

# clean-up last build
rm -rf build-ESP32_GENERIC-ROMFS

# ESP32 ROMFS
make BOARD=ESP32_GENERIC BOARD_VARIANT=ROMFS

echo "=========================================================="

