import logging
import os
import re

from typing import Any, Dict, List, Optional

import asyncsubprocess


MINER_CMD = '/opt/miner/bin/miner'
MINER_REGION_CMD = f'{MINER_CMD} info region'
MINER_PING_CMD = f'{MINER_CMD} ping'
MINER_ADD_GATEWAY_CMD = f'{MINER_CMD} txn add_gateway owner=%(owner)s --payer %(payer)s'
MINER_ASSERT_LOCATION_CMD = (
    f'{MINER_CMD} txn assert_location owner=%(owner)s location=%(location)s '
    f'--payer %(payer)s --nonce %(nonce)s'
)
MINER_RESTART_CMD = 'service miner restart'
MINER_TIMEOUT = 10  # Seconds
MINER_RESTART_TIMEOUT = 20  # Seconds
REG_FILE = '/var/lib/reg.conf'
CONF_FILE = '/data/etc/miner.conf'
SWARM_KEY_FILE = '/var/lib/user_swarm_key'


async def get_region() -> Optional[str]:
    try:
        output = await asyncsubprocess.check_output(MINER_REGION_CMD, timeout=MINER_TIMEOUT)
        if output.startswith('region_'):
            output = output[7:]
        if output == 'undefined':
            return

        return output.upper()
    except Exception:
        return


def get_cached_region() -> Optional[str]:
    try:
        with open(REG_FILE, 'rt') as f:
            return re.search(r'REGION=([a-zA-Z0-9]+)', f.read()).group(1)
    except Exception:
        pass


def is_swarm_key_mode() -> bool:
    return os.path.exists(SWARM_KEY_FILE)


async def ping() -> bool:
    try:
        output = await asyncsubprocess.check_output(MINER_PING_CMD, timeout=MINER_TIMEOUT)
    except Exception:
        return False

    return output == 'pong'


def get_config() -> Dict[str, Any]:
    current_config = {}
    bool_fields = set()

    if not os.path.exists(CONF_FILE):
        return current_config

    with open(CONF_FILE, 'rt') as f:
        for line in f:
            line = line.strip()

            try:
                k, v = line.split('=', 1)
            except ValueError:
                continue

            v = v.strip('"')
            k = k.lower()

            try:
                v = int(v)
            except ValueError:
                pass

            if k in bool_fields and isinstance(v, str):
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


async def restart() -> None:
    logging.info('restarting miner')
    try:
        await asyncsubprocess.check_call(MINER_RESTART_CMD, timeout=MINER_RESTART_TIMEOUT)
    except Exception:
        pass


async def txn_add_gateway(owner: str, payer: str) -> Optional[str]:
    logging.info('pushing add_gateway transaction to miner')

    cmd = MINER_ADD_GATEWAY_CMD % {'owner': owner, 'payer': payer}

    try:
        return await asyncsubprocess.check_output(cmd, timeout=MINER_TIMEOUT) or None
    except Exception:
        pass


async def txn_assert_location(owner: str, payer: str, location: str, nonce: int) -> Optional[str]:
    logging.info('pushing assert_location transaction to miner')

    cmd = MINER_ASSERT_LOCATION_CMD % {'owner': owner, 'payer': payer, 'location': location, nonce: nonce}

    try:
        return asyncsubprocess.check_output(cmd, timeout=MINER_TIMEOUT) or None
    except Exception:
        pass
