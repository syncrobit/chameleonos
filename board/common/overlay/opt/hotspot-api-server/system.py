
import logging
import os.path
import psutil
import subprocess

from typing import Any, Dict, Optional, Tuple


ETH_MAC_FILE = '/sys/class/net/eth0/address'
WLAN_MAC_FILE = '/sys/class/net/wlan0/address'
BT_MAC_CMD = 'hcitool dev | grep hci0 | cut -f 3'
BOARD_SN_CMD = '/etc/init.d/boardsn'
FW_VERSION_CMD = '/sbin/fwupdate current'
UPTIME_CMD = 'cat /proc/uptime | grep -oE "^[[:digit:]]+"'
REBOOT_CMD = '/sbin/reboot'
NET_TEST_CMD = '/sbin/nettest'
DATA_DIR = '/data'
CONFIG_TXT = '/boot/config.txt'
LAST_PANIC_FILE = '/var/lib/last_panic'

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


def remount_boot(rw: bool) -> None:
    how = ['ro', 'rw'][rw]
    logging.debug('remounting boot %s', how)
    subprocess.check_call(f'mount -o remount,{how} /boot', shell=True)


def get_rpi_sn() -> str:
    return subprocess.check_output(BOARD_SN_CMD, shell=True).decode().strip()


def get_os_prefix() -> str:
    return subprocess.check_output('source /etc/version && echo ${OS_PREFIX}', shell=True).decode().strip()


def reboot() -> None:
    logging.info('rebooting')
    os.system(REBOOT_CMD)


def factory_reset() -> None:
    logging.info('factory resetting')

    for service in FACTORY_RESET_SERVICES:
        try:
            logging.info('stopping %s', service)
            subprocess.check_output(f'service {service} stop', shell=True)

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


def get_bt_mac() -> Optional[str]:
    try:
        return subprocess.check_output(BT_MAC_CMD, shell=True).decode().strip().lower()

    except Exception:
        pass


def get_uptime() -> Optional[int]:
    try:
        return int(subprocess.check_output(UPTIME_CMD, shell=True).decode().strip())

    except Exception:
        pass


def get_fw_version() -> Optional[str]:
    try:
        return subprocess.check_output(FW_VERSION_CMD, shell=True).decode().strip()

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


def get_temperature() -> int:
    return int(psutil.sensors_temperatures()['cpu_thermal'][0].current)


def net_test(download_speed: bool = True, latency: bool = True, public_ip: bool = True) -> Dict[str, Any]:
    result = {
        'download_speed': None,
        'latency': None,
        'public_ip': None
    }

    cmd = NET_TEST_CMD
    if download_speed:
        cmd += ' --download-speed'
    if latency:
        cmd += ' --latency'
    if public_ip:
        cmd += ' --public-ip'

    try:
        output = subprocess.check_output(cmd, shell=True).decode().strip()

    except Exception:
        return result

    for line in output.split('\n'):
        parts = line.split(':', 1)
        if len(parts) < 2:
            continue

        key, value = parts
        key = key.strip().lower().replace(' ', '_')
        value = value.strip()

        # Decode numeric values
        if key in ('download_speed', 'latency'):
            value = float(value.split()[0]) or None
            if value > 10:
                value = int(value)

        result[key] = value

    return result


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
            details[name] = value

    return details


def is_ext_wifi_antenna_enabled() -> bool:
    with open(CONFIG_TXT, 'rt') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line == 'dtparam=ant2':
                return True

    return False


def set_ext_wifi_antenna_enabled(enabled: bool) -> None:
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

    remount_boot(rw=True)
    with open(CONFIG_TXT, 'wt') as f:
        f.writelines(modified_lines)
    remount_boot(rw=False)
