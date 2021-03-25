#!/bin/bash

source /var/run/hardware.conf

gpio.sh ${LGW_RESET_GPIO} 0
usleep 100000
gpio.sh ${LGW_RESET_GPIO} 1
usleep 100000
gpio.sh ${LGW_RESET_GPIO} 0
usleep 100000
