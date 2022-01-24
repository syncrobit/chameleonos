#!/bin/bash

source /var/run/hardware.conf

IFS=, GPIOS=(${LGW_RESET_GPIO}); unset IFS

for gpio in ${GPIOS[@]}; do
    raspi-gpio set ${gpio} op dl
    usleep 100000
    raspi-gpio set ${gpio} op dh
    usleep 100000
    raspi-gpio set ${gpio} op dl
    usleep 100000
done
