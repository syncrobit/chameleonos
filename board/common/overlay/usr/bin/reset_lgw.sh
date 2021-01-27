#!/bin/bash

RESET_GPIO=17

gpio.sh ${RESET_GPIO} 0
usleep 100000
gpio.sh ${RESET_GPIO} 1
usleep 100000
gpio.sh ${RESET_GPIO} 0
usleep 100000
