#!/bin/bash

cd $(dirname $0)
set -e
set -a

if [[ -z "${VERSION}" ]]; then
    echo "VERSION variable is unset"
    exit 1
fi

if [[ -z "$1" ]]; then
    echo "Missing first argument"
    exit 1
fi

if [[ -z "${VENDORS}" ]]; then
    VENDORS=$(ls -1 vendors/ | sed s/.conf//)
fi

set -a
for VENDOR in ${VENDORS}; do
    source vendors/${VENDOR}.conf
    for PLATFORM in ${PLATFORMS}; do
        echo "Deploying ${VENDOR}/${PLATFORM}"
        ./deploy.sh $1 output/${PLATFORM}/images/chameleonos-${THINGOS_PREFIX}-${PLATFORM}-${VERSION}.img.xz
    done
done
