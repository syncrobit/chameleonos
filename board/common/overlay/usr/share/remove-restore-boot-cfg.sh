#!/bin/bash

mount -o remount,rw /
if [[ -f /usr/libexec/fw-restore-boot-cfg ]]; then
    rm /usr/libexec/fw-restore-boot-cfg
fi
