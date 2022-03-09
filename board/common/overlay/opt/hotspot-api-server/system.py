
import logging
import os.path
import psutil

from typing import Dict, Optional, Tuple

import asyncsubprocess


ETH_MAC_FILE = '/sys/class/net/eth0/address'
WLAN_MAC_FILE = '/sys/class/net/wlan0/address'
BT_MAC_CMD = 'timeout 1 bluetoothctl list | grep -oE "[A-F0-9:]+{17}"'
BOARD_SN_CMD = '/etc/init.d/boardsn'
FW_VERSION_CMD = '/sbin/fwupdate current'
UPTIME_CMD = 'cat /proc/uptime | grep -oE "^[[:digit:]]+"'
REBOOT_CMD = '/sbin/reboot'
DATA_DIR = '/data'
CONFIG_TXT = '/boot/config.txt'
LAST_PANIC_FILE = '/var/lib/last_panic'
OS_CONF = '/data/etc/os.conf'

LOG_DIR = '/var/log'
MINER_DATA_DIR = '/var/lib/miner'
FACTORY_RESET_SERVICES = ['miner', 'packetforwarder', 'gatewayconfig', 'connman']
FACTORY_RESET_CONF_FILES = [
    '/var/lib/reg.conf',
    '/data/etc/miner.conf',
    '/data/etc/packet_forwarder.conf'
    '/data/etc/ledstrip.conf'
]
FACTORY_RESET_CONNMAN_PATH_PREFIXES = [
    '/var/lib/connman/wifi_*',
    '/var/lib/connman/ethernet_*'
]


async def remount_boot(rw: bool) -> None:
    how = ['ro', 'rw'][rw]
    logging.debug('remounting boot %s', how)
    await asyncsubprocess.check_call(f'mount -o remount,{how} /boot')


async def get_rpi_sn() -> str:
    return await asyncsubprocess.check_output(BOARD_SN_CMD)


async def get_os_prefix() -> str:
    return await asyncsubprocess.check_output('source /etc/version && echo ${OS_PREFIX}')


def reboot() -> None:
    logging.info('rebooting')
    os.system(REBOOT_CMD)


async def factory_reset() -> None:
    logging.info('factory resetting')

    for service in FACTORY_RESET_SERVICES:
        try:
            logging.info('stopping %s', service)
            await asyncsubprocess.check_call(f'service {service} stop')
        except Exception:
            pass

    for file in FACTORY_RESET_CONF_FILES:
        logging.info('removing %s', file)
        os.system(f'rm -f {file}')

    logging.info('removing network settings')
    for prefix in FACTORY_RESET_CONNMAN_PATH_PREFIXES:
        os.system(f'rm -rf {prefix}')

    logging.info('removing log files')
    os.system(f'rm -rf {LOG_DIR}/*')

    logging.info('removing miner data')
    os.system(f'rm -rf {MINER_DATA_DIR}')

    logging.info('rebooting')
    os.system(REBOOT_CMD)


def get_eth_mac() -> Optional[str]:
    try:
        with open(ETH_MAC_FILE, 'rt') as f:
            return f.read().strip()
    except Exception:
        pass


def get_wlan_mac() -> Optional[str]:
    try:
        with open(WLAN_MAC_FILE, 'rt') as f:
            return f.read().strip()
    except Exception:
        pass


async def get_bt_mac() -> Optional[str]:
    try:
        return (await asyncsubprocess.check_output(BT_MAC_CMD)).lower()
    except Exception:
        pass


async def get_uptime() -> Optional[int]:
    try:
        return int(await asyncsubprocess.check_output(UPTIME_CMD))
    except Exception:
        pass


async def get_fw_version() -> Optional[str]:
    try:
        return await asyncsubprocess.check_output(FW_VERSION_CMD)
    except Exception:
        pass


def get_cpu_usage() -> float:
    return psutil.cpu_percent()


def get_mem_info() -> Tuple[int, int]:
    vm = psutil.virtual_memory()
    return int(vm.used / 1024 / 1024), int(vm.total / 1024 / 1024)


def get_swap_info() -> Tuple[int, int]:
    sm = psutil.swap_memory()
    return int(sm.used / 1024 / 1024), int(sm.total / 1024 / 1024)


def get_storage_info() -> Tuple[int, int]:
    du = psutil.disk_usage(DATA_DIR)
    return int(du.used / 1024 / 1024), int(du.total / 1024 / 1024)


def get_temperature() -> Optional[int]:
    try:
        return int(psutil.sensors_temperatures()['cpu_thermal'][0].current)
    except Exception:
        pass


def get_last_panic_details() -> Optional[Dict[str, str]]:
    if not os.path.exists(LAST_PANIC_FILE):
        return

    details = {}

    with open(LAST_PANIC_FILE, 'rt') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split('=')
            if len(parts) != 2:
                continue

            name, value = parts
            value = value.strip('"')
            if name in ('timestamp', 'uptime'):
                value = int(value)

            details[name] = value

    return details


async def get_os_conf_var(name: str) -> str:
    cmd = f'source /etc/init.d/os_conf && echo ${{{name}}}'
    return await asyncsubprocess.check_output(cmd)


def set_os_conf_var(name: str, value: str) -> None:
    if os.path.exists(OS_CONF):
        with open(OS_CONF, 'rt') as f:
            lines = f.readlines()
            lines = [line.strip() for line in lines if line.strip()]
    else:
        lines = []

    variables = [line.split('=', 1) for line in lines]
    variables = {k: v.strip('"') for k, v in variables}
    variables[name] = value

    lines = [f'{k}="{v}"\n' for k, v in variables.items()]

    with open(OS_CONF, 'wt') as f:
        f.writelines(lines)


async def is_periodic_reboot_enabled() -> bool:
    return (await get_os_conf_var('OS_PERIODIC_REBOOT')) != 'false'


def set_periodic_reboot_enabled(enabled: bool) -> None:
    set_os_conf_var('OS_PERIODIC_REBOOT', str(enabled).lower())


def is_ext_wifi_antenna_enabled() -> bool:
    with open(CONFIG_TXT, 'rt') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line == 'dtparam=ant2':
                return True

    return False


async def set_ext_wifi_antenna_enabled(enabled: bool) -> None:
    if is_ext_wifi_antenna_enabled() == enabled:
        return  # We're already there

    logging.debug('%s external Wi-Fi antenna', ['disabling', 'enabling'][enabled])

    with open(CONFIG_TXT, 'rt') as f:
        lines = f.readlines()

    modified_lines = []
    found = False
    for line in lines:
        if line.strip() == 'dtparam=ant2':
            found = True
            if not enabled:
                continue

        modified_lines.append(line)

    if enabled and not found:
        modified_lines.append('dtparam=ant2\n')

    await remount_boot(rw=True)
    with open(CONFIG_TXT, 'wt') as f:
        f.writelines(modified_lines)
    await remount_boot(rw=False)
