
from typing import Any, Dict, Optional

import logging
import re
import subprocess


MINER_HEIGHT_CMD = '/opt/miner/bin/miner info height'
MINER_LISTEN_ADDR_CMD = '/opt/miner/bin/miner peer book -s | grep listen_addrs -A2 | tail -n1 | tr -d "|"'
MINER_RESTART_CMD = 'service miner restart'
REG_FILE = '/var/lib/reg.conf'
NAT_FILE = '/data/etc/nat.conf'


def get_height() -> Optional[int]:
    try:
        info_height = subprocess.check_output(MINER_HEIGHT_CMD, shell=True)
        return int(info_height.decode().split()[1])

    except Exception:
        pass


def get_listen_addr() -> Optional[str]:
    try:
        return subprocess.check_output(MINER_LISTEN_ADDR_CMD, shell=True).decode().strip()

    except Exception:
        pass


def get_region() -> Optional[str]:
    try:
        with open(REG_FILE, 'rt') as f:
            return re.search(r'REGION=([a-zA-Z0-9])', f.read()).group(1)
    except Exception:
        pass


def get_nat_config() -> Dict[str, Any]:
    nat = {
        'external_ip': None,
        'external_port': None,
        'internal_port': None
    }

    with open(NAT_FILE, 'rt') as f:
        for line in f:
            line = line.strip()
            try:
                k, v = line.split('=', 1)

            except ValueError:
                continue

            k = k[4:].lower()  # Skip NAT_
            if k.endswith('port'):
                try:
                    v = int(v)

                except ValueError:
                    continue

            nat[k] = v

    return nat


def set_nat_config(nat: Dict[str, Any]) -> None:
    logging.info('updating NAT config: %s', nat)

    # Use current values for missing entries
    current_nat = get_nat_config()
    for k, v in current_nat.items():
        nat.setdefault(k, v)

    with open(NAT_FILE, 'wt') as f:
        for k, v in nat.items():
            if v is None:
                continue

            k = f'NAT_{k.upper()}'
            line = f'{k}={v}\n'
            f.write(line)


def restart() -> None:
    subprocess.check_output(MINER_RESTART_CMD, shell=True)
