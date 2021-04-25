
from typing import Any, Dict, Optional

import logging
import re
import subprocess


PF_RESTART_CMD = 'service packetforwarder restart'
PF_CONCENTRATOR_MODEL_CMD = 'ps aux | grep /opt/packet_forwarder/bin/lora_pkt_fwd_ | grep -v grep'
CONF_FILE = '/data/etc/packet_forwarder.conf'


def get_concentrator_model() -> Optional[str]:
    try:
        output = subprocess.check_output(PF_CONCENTRATOR_MODEL_CMD, shell=True)
        prog_path = output.split()[-1].decode()
        return re.search(r'sx\d+', prog_path).group()

    except Exception:
        pass


def get_config() -> Dict[str, Any]:
    config = {
        'antenna_gain': None,
        'rssi_offset': None,
        'tx_power': None
    }

    with open(CONF_FILE, 'rt') as f:
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
                    continue

            config[k] = v

    return config


def set_config(config: Dict[str, Any]) -> None:
    logging.info('updating PF config: %s', config)

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


def restart() -> None:
    subprocess.check_output(PF_RESTART_CMD, shell=True)
