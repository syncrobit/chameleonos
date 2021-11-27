
from typing import Any, Dict, List, Optional

import logging
import os
import re
import subprocess


MINER_CMD = '/opt/miner/bin/miner'
MINER_HEIGHT_CMD = f'{MINER_CMD} info height'
MINER_REGION_CMD = f'{MINER_CMD} info region'
MINER_LISTEN_ADDR_CMD = f'{MINER_CMD} peer book -s | grep "listen_addrs (prioritized)" -A2 | tail -n1 | tr -d "|"'
MINER_PING_CMD = f'{MINER_CMD} ping'
MINER_PEER_BOOK_CMD = f"{MINER_CMD} peer book -s | grep -E '^\\|([^\\|]+\\|){{4}}$' | tail -n +2"
MINER_RESET_PEER_BOOK_CMD = "/sbin/resetpeers"
MINER_PEER_PING_CMD = f'{MINER_CMD} peer ping /p2p/%(address)s'
MINER_PEER_CONNECT_CMD = f'{MINER_CMD} peer connect /p2p/%(address)s'
MINER_ADD_GATEWAY_CMD = f'{MINER_CMD} txn add_gateway owner=%(owner)s --payer %(payer)s'
MINER_ASSERT_LOCATION_CMD = (
    f'{MINER_CMD} txn assert_location owner=%(owner)s location=%(location)s '
    f'--payer %(payer)s --nonce %(nonce)s'
)
MINER_RESTART_CMD = 'service miner restart'
MINER_TIMEOUT = 10  # Seconds
REG_FILE = '/var/lib/reg.conf'
CONF_FILE = '/data/etc/miner.conf'
FORCE_SYNC_FILE = '/var/lib/miner/force_sync'
SWARM_KEY_FILE = '/var/lib/user_swarm_key'


def get_height() -> Optional[int]:
    try:
        info_height = subprocess.check_output(MINER_HEIGHT_CMD, shell=True, timeout=MINER_TIMEOUT)
        return int(info_height.decode().split()[1])
    except Exception:
        pass


def get_listen_addr() -> Optional[str]:
    try:
        output = subprocess.check_output(MINER_LISTEN_ADDR_CMD, shell=True, timeout=MINER_TIMEOUT)
        return output.decode().strip() or None
    except Exception:
        pass


def get_region(direct: bool = False) -> Optional[str]:
    if direct:
        try:
            output = subprocess.check_output(MINER_REGION_CMD, shell=True, timeout=MINER_TIMEOUT).decode().strip()
            if output == 'undefined':
                return

            return output
        except Exception:
            return

    try:
        with open(REG_FILE, 'rt') as f:
            return re.search(r'REGION=([a-zA-Z0-9]+)', f.read()).group(1)
    except Exception:
        pass


def is_swarm_key_mode() -> bool:
    return os.path.exists(SWARM_KEY_FILE)


def ping() -> bool:
    try:
        output = subprocess.check_output(MINER_PING_CMD, shell=True, timeout=MINER_TIMEOUT).decode().strip()
    except subprocess.SubprocessError:
        return False

    return output == 'pong'


def get_peer_book() -> List[Dict[str, str]]:
    try:
        output = subprocess.check_output(MINER_PEER_BOOK_CMD, shell=True, timeout=MINER_TIMEOUT).decode()
    except subprocess.SubprocessError:
        return []

    lines = output.split('\n')
    lines = [line.strip().strip('|').split('|') for line in lines if line.strip()]
    return [
        {
            'local': line[0].strip(),
            'remote': line[1].strip(),
            'p2p': line[2].strip(),
            'address': line[2].strip().replace('/p2p/', ''),
            'name': line[3].strip(),
        }
        for line in lines
    ]


def reset_peer_book() -> None:
    subprocess.check_call(MINER_RESET_PEER_BOOK_CMD, shell=True, timeout=MINER_TIMEOUT * 2, stdout=subprocess.DEVNULL)


def ping_peer(address: str) -> Optional[int]:
    cmd = MINER_PEER_PING_CMD % {'address': address}
    try:
        output = subprocess.check_output(cmd, shell=True, timeout=MINER_TIMEOUT).decode().strip()
    except subprocess.SubprocessError:
        return

    match = re.match(r'.*?(\d+) ms$', output)
    if match:
        return int(match.group(1))


def connect_peer(address: str) -> bool:
    cmd = MINER_PEER_CONNECT_CMD % {'address': address}
    try:
        output = subprocess.check_output(cmd, shell=True, timeout=MINER_TIMEOUT).decode().strip()
    except subprocess.SubprocessError:
        return False

    return output.startswith('Connected')


def get_config() -> Dict[str, Any]:
    current_config = {
        'nat_external_ip': None,
        'nat_external_port': None,
        'nat_internal_port': None,
        'panic_on_relayed': False,
        'panic_on_unreachable': False,
        'force_sync_enabled': True,
        'periodic_reset_peers': False,
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

            k = k.lower()

            if k.endswith('port'):
                try:
                    v = int(v)
                except ValueError:
                    continue

            if k.startswith('panic_on') or k.endswith('enabled'):
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
    logging.info('forcing miner sync')

    if os.path.exists(os.path.dirname(FORCE_SYNC_FILE)):
        with open(FORCE_SYNC_FILE, 'w'):
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
