#!/bin/bash

source /var/run/hardware.conf

IFS=, GPIOS=(${LGW_RESET_GPIO}); unset IFS

for gpio in ${GPIOS[@]}; do
    gpio.sh ${gpio} 0
    usleep 100000
    gpio.sh ${gpio} 1
    usleep 100000
    gpio.sh ${gpio} 0
    usleep 100000
done
