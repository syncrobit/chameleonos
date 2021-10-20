
from typing import Any, Dict, Optional

import logging
import os
import subprocess


RESTART_CMD = 'service ledstate restart'
CONF_FILE = '/data/etc/ledstrip.conf'
SYS_CONF_FILE = '/etc/ledstrip.conf'
STATE_FILE = '/var/run/led_state'
DEF_STATE = 'powered_up'


def get_current_state() -> str:
    try:
        with open(STATE_FILE, 'rt') as f:
            return f.read().strip()
    except Exception:
        return DEF_STATE


def get_config(conf_file: Optional[str] = None) -> Dict[str, Any]:
    if conf_file is None:
        config = get_config(SYS_CONF_FILE)
        conf_file = CONF_FILE

    else:
        config = {
            'brightness': 50,
            'ok_color': 'green'
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

            k = k[10:].lower()  # Skip LED_STRIP_
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
    logging.info('updating ledstrip config: %s', config)

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

            k = f'LED_STRIP_{k.upper()}'
            line = f'{k}={v}\n'
            f.write(line)


def restart() -> None:
    logging.info('restarting ledstrip')
    subprocess.check_call(RESTART_CMD, shell=True)
