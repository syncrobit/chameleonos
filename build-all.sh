#!/bin/bash

cd $(dirname $0)
set -e
set -a

if [[ -z "${VERSION}" ]]; then
    echo "VERSION variable is unset"
    exit 1
fi

VENDORS=$(ls -1 vendors/ | sed s/.conf//)

export THINGOS_VERSION=${VERSION}

for VENDOR in ${VENDORS}; do
    echo "Building for ${VENDOR}"
    ./build.sh raspberrypi4arm64
    ./build.sh raspberrypi4arm64 mkimage
    ./build.sh raspberrypi4arm64 mkrelease
done
