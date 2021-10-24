#!/bin/bash

set -e

export TARGET="$1"
export BOARD=$(basename $(dirname ${TARGET}))
export COMMON_DIR=$(dirname $0)
export BOARD_DIR=${COMMON_DIR}/../${BOARD}
export BOOT_DIR=${TARGET}/../images/boot/
export IMG_DIR=${TARGET}/../images

mkdir -p ${BOOT_DIR}

if [ -x ${BOARD_DIR}/postscript.sh ]; then
    ${BOARD_DIR}/postscript.sh
fi

# cleanups
${COMMON_DIR}/cleanups.sh
if [ -x ${BOARD_DIR}/cleanups.sh ]; then
    ${BOARD_DIR}/cleanups.sh
fi

# transform /var contents as needed
rm -rf ${TARGET}/var/cache
rm -rf ${TARGET}/var/lib
rm -rf ${TARGET}/var/lock
rm -rf ${TARGET}/var/log
rm -rf ${TARGET}/var/run
rm -rf ${TARGET}/var/spool
rm -rf ${TARGET}/var/tmp

ln -s /tmp ${TARGET}/var/cache
ln -s /tmp ${TARGET}/var/lock
ln -s /tmp ${TARGET}/var/run
ln -s /tmp ${TARGET}/var/spool
ln -s /tmp ${TARGET}/var/tmp
ln -s /tmp ${TARGET}/run
mkdir -p ${TARGET}/var/lib
mkdir -p ${TARGET}/var/log

# board-specific os.conf
if [ -r ${BOARD_DIR}/os.conf ]; then
    for line in $(cat ${BOARD_DIR}/os.conf); do
        key=$(echo ${line} | cut -d '=' -f 1)
        sed -i -r "s/${key}=.*/${line}/" /${TARGET}/etc/os.conf
    done
fi

# add admin user alias
if ! grep -qE '^admin:' ${TARGET}/etc/passwd; then
    echo "admin:x:0:0:root:/root:/bin/sh" >> ${TARGET}/etc/passwd
fi

# adjust root password
if [[ -n "${THINGOS_ROOT_PASSWORD_HASH}" ]] && [[ -f ${TARGET}/etc/shadow ]]; then
    echo "Updating root password hash"
    sed -ri "s,root:[^:]+:,root:${THINGOS_ROOT_PASSWORD_HASH}:," ${TARGET}/etc/shadow
    sed -ri "s,admin:[^:]+:,admin:${THINGOS_ROOT_PASSWORD_HASH}:," ${TARGET}/etc/shadow
fi

# set vendor-default hardware settings
if [[ -n "${LGW_RESET_GPIO}" ]]; then
    echo "Using LGW_RESET_GPIO=${LGW_RESET_GPIO}"
    sed -ri "s/DEFAULT_LGW_RESET_GPIO=.*/DEFAULT_LGW_RESET_GPIO=${LGW_RESET_GPIO}/" ${TARGET}/etc/init.d/S*hwdetect
else
    echo "Using default LGW_RESET_GPIO"
fi
if [[ -n "${PAIR_BUTTON_GPIO}" ]]; then
    echo "Using PAIR_BUTTON_GPIO=${PAIR_BUTTON_GPIO}"
    sed -ri "s/DEFAULT_PAIR_BUTTON_GPIO=.*/DEFAULT_PAIR_BUTTON_GPIO=${PAIR_BUTTON_GPIO}/" ${TARGET}/etc/init.d/S*hwdetect
else
    echo "Using default PAIR_BUTTON_GPIO"
fi
if [[ -n "${PAIR_BUTTON_ACTIVE_LEVEL}" ]]; then
    echo "Using PAIR_BUTTON_ACTIVE_LEVEL=${PAIR_BUTTON_ACTIVE_LEVEL}"
    sed -ri "s/DEFAULT_PAIR_BUTTON_ACTIVE_LEVEL=.*/DEFAULT_PAIR_BUTTON_ACTIVE_LEVEL=${PAIR_BUTTON_ACTIVE_LEVEL}/" ${TARGET}/etc/init.d/S*hwdetect
else
    echo "Using default PAIR_BUTTON_ACTIVE_LEVEL"
fi
if [[ -n "${ECC_ADDRESS}" ]]; then
    echo "Using ECC_ADDRESS=${ECC_ADDRESS}"
    sed -ri "s/DEFAULT_ECC_ADDRESS=.*/DEFAULT_ECC_ADDRESS=${ECC_ADDRESS}/" ${TARGET}/etc/init.d/S*hwdetect
else
    echo "Using default ECC_ADDRESS"
fi
if [[ -n "${ECC_SLOT}" ]]; then
    echo "Using ECC_SLOT=${ECC_SLOT}"
    sed -ri "s/DEFAULT_ECC_SLOT=.*/DEFAULT_ECC_SLOT=${ECC_SLOT}/" ${TARGET}/etc/init.d/S*hwdetect
else
    echo "Using default ECC_SLOT"
fi
