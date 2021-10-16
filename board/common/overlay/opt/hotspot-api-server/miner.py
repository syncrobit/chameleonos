
from typing import Any, Dict, Optional

import aiohttp
import logging
import os
import re
import subprocess


MINER_CMD = '/opt/miner/bin/miner'
MINER_HEIGHT_CMD = f'{MINER_CMD} info height'
MINER_LISTEN_ADDR_CMD = f'{MINER_CMD} peer book -s | grep " listen_addrs" -A2 | tail -n1 | tr -d "|"'
MINER_ADD_GATEWAY_CMD = f'{MINER_CMD} txn add_gateway owner=%(owner)s --payer %(payer)s'
MINER_ASSERT_LOCATION_CMD = f'{MINER_CMD} txn assert_location owner=%(owner)s location=%(location)s ' \
                            f'--payer %(payer)s --nonce %(nonce)s'
MINER_RESTART_CMD = 'service miner restart'
MINER_TIMEOUT = 10  # Seconds
REG_FILE = '/var/lib/reg.conf'
CONF_FILE = '/data/etc/nat.conf'
FORCE_RESYNC_FILE = '/var/lib/miner/force_resync'
NO_SYNC_FILE = '/data/etc/miner_no_sync'
SWARM_KEY_FILE = '/var/lib/user_swarm_key'


def get_height() -> Optional[int]:
    try:
        info_height = subprocess.check_output(MINER_HEIGHT_CMD, shell=True, timeout=MINER_TIMEOUT)
        return int(info_height.decode().split()[1])

    except Exception:
        pass


async def get_blockchain_height() -> int:
    url = 'https://api.helium.io/v1/blocks/height'
    async with aiohttp.ClientSession() as client:
        async with client.request(method='GET', url=url) as response:
            return (await response.json())['data']['height']


def get_listen_addr() -> Optional[str]:
    try:
        output = subprocess.check_output(MINER_LISTEN_ADDR_CMD, shell=True, timeout=MINER_TIMEOUT)
        return output.decode().strip() or None

    except Exception:
        pass


def get_region() -> str:
    try:
        with open(REG_FILE, 'rt') as f:
            return re.search(r'REGION=([a-zA-Z0-9]+)', f.read()).group(1)

    except Exception:
        pass


def is_swarm_key_mode() -> bool:
    return os.path.exists(SWARM_KEY_FILE)


def get_config() -> Dict[str, Any]:
    current_config = {
        'nat_external_ip': None,
        'nat_external_port': None,
        'nat_internal_port': None,
        'panic_on_relayed': False,
        'panic_on_unreachable': False
    }

    if not os.path.exists(CONF_FILE):
        return current_config

    with open(CONF_FILE, 'rt') as f:
        for line in f:
            line = line.strip()
            try:
                k, v = line.split('=', 1)

            except ValueError:
                continue

            if k.endswith('port'):
                try:
                    v = int(v)

                except ValueError:
                    continue

            if k.startswith('panic_on'):
                v = v.lower() == 'true'

            current_config[k] = v

    return current_config


def set_config(config: Dict[str, Any]) -> None:
    logging.info('updating miner config: %s', config)

    # Use current values for missing entries
    current_config = get_config()
    for k, v in current_config.items():
        config.setdefault(k, v)

    with open(CONF_FILE, 'wt') as f:
        for k, v in config.items():
            if v is None:
                continue

            if isinstance(v, str):  # Strip spaces, preventing some cases of invalid IP addresses
                v = v.strip()
            elif isinstance(v, bool):
                v = str(v).lower()

            k = k.upper()
            line = f'{k}={v}\n'
            f.write(line)


def resync() -> None:
    logging.info('forcing miner resync')

    if os.path.exists(os.path.dirname(FORCE_RESYNC_FILE)):
        with open(FORCE_RESYNC_FILE, 'w'):
            pass

    restart()


def restart() -> None:
    logging.info('restarting miner')
    try:
        subprocess.check_call(MINER_RESTART_CMD, shell=True, timeout=MINER_TIMEOUT)

    except Exception:
        pass


def txn_add_gateway(owner: str, payer: str) -> Optional[str]:
    logging.info('pushing add_gateway transaction to miner')

    cmd = MINER_ADD_GATEWAY_CMD % {'owner': owner, 'payer': payer}

    try:
        output = subprocess.check_output(cmd, shell=True, timeout=MINER_TIMEOUT)
        return output.decode().strip() or None

    except Exception:
        pass


def txn_assert_location(owner: str, payer: str, location: str, nonce: int) -> Optional[str]:
    logging.info('pushing assert_location transaction to miner')

    cmd = MINER_ASSERT_LOCATION_CMD % {'owner': owner, 'payer': payer, 'location': location, nonce: nonce}

    try:
        output = subprocess.check_output(cmd, shell=True, timeout=MINER_TIMEOUT)
        return output.decode().strip() or None

    except Exception:
        pass
