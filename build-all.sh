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
    source vendors/${VENDOR}.conf
    for PLATFORM in ${PLATFORMS}; do
        echo "Building ${VENDOR}/${PLATFORM}"
        rm -f output/${PLATFORM}/.config
        ./build.sh ${PLATFORM}
        sudo -E ./build.sh ${PLATFORM} mkimage
        ./build.sh ${PLATFORM} mkrelease
    done
done
