#!/bin/bash
# setup.sh

arduino-cli compile --quiet --build-path ./build -b esp32:esp32:esp32 ./l_chika.ino

HOST=$1

scp ./build/*.bin $HOST:/tmp/

ssh $HOST "arduino-cli config init --overwrite &&
            arduino-cli config add board_manager.additional_urls https://dl.espressif.com/dl/package_esp32_index.json &&
            arduino-cli core update-index &&
            arduino-cli core install esp32:esp32 &&
            arduino-cli upload --input-file /tmp/l_chika.ino.bin -p /dev/ttyATM0 -b esp32:esp32:esp32"

if [ $? -eq 0 ]; then
    echo "成功したよ"
fi