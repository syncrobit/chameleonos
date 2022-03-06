#!/bin/bash

source /var/run/hardware.conf

IFS=, GPIOS=(${LGW_RESET_GPIO}); unset IFS

for gpio in ${GPIOS[@]}; do
    gpio-do ${gpio} set 0
    usleep 100000
    gpio-do ${gpio} set 1
    usleep 100000
    gpio-do ${gpio} set 0
    usleep 100000
done
