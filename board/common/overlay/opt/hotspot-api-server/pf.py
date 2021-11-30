
import logging
import os
import re

from typing import Any, Dict, Optional

import asyncsubprocess
import miner


PF_RESTART_CMD = 'service packetforwarder restart'
PF_CONCENTRATOR_MODEL_CMD = 'ps aux | grep /lora_pkt_fwd_ | grep -v grep'
PF_CONCENTRATOR_ID_CMD = 'cd /opt/packet_forwarder/bin/ && ./chip_id | grep -oE "0x[a-f0-9]+" | cut -b 3-100'
CONF_FILE = '/data/etc/packet_forwarder.conf'
SYS_CONF_FILE = '/etc/packet_forwarder.conf'
PF_STARTUP_SCRIPT = '/etc/init.d/S86packetforwarder'
PF_TIMEOUT = 10  # Seconds
DEF_REGION = 'US915'


async def get_concentrator_id() -> Optional[str]:
    try:
        return await asyncsubprocess.check_output(PF_CONCENTRATOR_ID_CMD)

    except Exception:
        pass


async def get_concentrator_model() -> Optional[str]:
    try:
        output = await asyncsubprocess.check_output(PF_CONCENTRATOR_MODEL_CMD)
        prog_path = output.split()[-1]
        return re.search(r'sx\d+', prog_path).group()

    except Exception:
        pass


def get_def_tx_power(region: str) -> int:
    with open(PF_STARTUP_SCRIPT, 'rt') as f:
        data = f.read()

    def_powers = re.search(r'DEF_TX_POWER=\((.*?)\)', data, flags=re.DOTALL).group(1).split()
    def_powers = [i for i in def_powers if i.startswith('[')]
    def_powers = [i.split('=', 1) for i in def_powers]
    def_powers = {i[0][1:-1]: int(i[1]) for i in def_powers}

    return def_powers.get(region)


def get_config(conf_file: Optional[str] = None) -> Dict[str, Any]:
    if conf_file is None:
        config = get_config(SYS_CONF_FILE)
        conf_file = CONF_FILE

        config['tx_power'] = get_def_tx_power(miner.get_cached_region() or DEF_REGION)

    else:
        config = {
            'antenna_gain': None,
            'rssi_offset': None,
            'tx_power': None
        }

    if not os.path.exists(conf_file):
        return config

    with open(conf_file, 'rt') as f:
        for line in f:
            line = line.strip()
            try:
                k, v = line.split('=', 1)

            except ValueError:
                continue

            k = k[3:].lower()  # Skip PF_
            try:
                v = int(v)

            except ValueError:
                try:
                    v = float(v)

                except ValueError:
                    pass

            config[k] = v

    return config


def set_config(config: Dict[str, Any]) -> None:
    logging.info('updating packet-forwarder config: %s', config)

    # Use default values for null entries
    default_config = get_config(SYS_CONF_FILE)
    for k, v in config.items():
        if v is None:
            config[k] = default_config[k]

    # Use current values for missing entries
    current_config = get_config()
    for k, v in current_config.items():
        config.setdefault(k, v)

    with open(CONF_FILE, 'wt') as f:
        for k, v in config.items():
            if v is None:
                continue

            k = f'PF_{k.upper()}'
            line = f'{k}={v}\n'
            f.write(line)


async def restart() -> None:
    logging.info('restarting packet-forwarder')
    await asyncsubprocess.check_call(PF_RESTART_CMD, timeout=PF_TIMEOUT)
