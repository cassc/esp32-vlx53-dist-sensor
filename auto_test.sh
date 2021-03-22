#!/bin/bash

# make upload
esptool.py --chip esp32 --port "/dev/ttyUSB0" --baud 460800 --before default_reset --after hard_reset write_flash -z --flash_mode dio --flash_freq 40m --flash_size detect 0x1000 /home/garfield/.platformio/packages/framework-arduinoespressif32/tools/sdk/bin/bootloader_dio_40m.bin 0x8000 /opt/garfield/projects/platformio/ESP32-TOF/.pio/build/featheresp32/partitions.bin 0xe000 /home/garfield/.platformio/packages/framework-arduinoespressif32/tools/partitions/boot_app0.bin 0x10000 .pio/build/featheresp32/firmware.bin
sleep 2s
python3 validate_dist.py
