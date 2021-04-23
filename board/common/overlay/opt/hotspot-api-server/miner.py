
from typing import Optional

import re
import subprocess


MINER_HEIGHT_CMD = '/opt/miner/bin/miner info height'
MINER_LISTEN_ADDR_CMD = '/opt/miner/bin/miner peer book -s | grep listen_addrs -A2 | tail -n1 | tr -d "|"'


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
