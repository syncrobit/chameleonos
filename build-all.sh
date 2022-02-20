#!/bin/bash

cd $(dirname $0)
set -e
set -a

if [[ -z "${VERSION}" ]]; then
    echo "VERSION variable is unset"
    exit 1
fi

if [[ -z "${VENDORS}" ]]; then
    VENDORS=$(ls -1 vendors/ | sed s/.conf//)
fi

export THINGOS_VERSION=${VERSION}

for VENDOR in ${VENDORS}; do
    echo "Building for ${VENDOR}"
    ./build.sh raspberrypi64
    sudo ./build.sh raspberrypi64 mkimage
    ./build.sh raspberrypi64 mkrelease
done
