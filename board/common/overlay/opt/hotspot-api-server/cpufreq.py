
import logging
import os

from typing import Any, Dict, Optional

import asyncsubprocess


RESTART_CMD = 'service cpufreq start'
CONF_FILE = '/data/etc/cpufreq.conf'
SYS_CONF_FILE = '/etc/cpufreq.conf'


def get_config(conf_file: Optional[str] = None) -> Dict[str, Any]:
    if conf_file is None:
        config = get_config(SYS_CONF_FILE)
        conf_file = CONF_FILE

    else:
        config = {
            'governor': None,
            'min': None,
            'max': None
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

            k = k[9:].lower()  # Skip CPU_FREQ_
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
    logging.info('updating cpufreq config: %s', config)

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

            k = f'CPU_FREQ_{k.upper()}'
            line = f'{k}={v}\n'
            f.write(line)


async def restart() -> None:
    logging.info('restarting cpufreq')
    await asyncsubprocess.check_call(RESTART_CMD)
