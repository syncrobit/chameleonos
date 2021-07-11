import time

from typing import Any, Dict

import logging
import subprocess


STATUS_CMD = 'fwupdate status'
LATEST_CMD = 'fwupdate-check --info'
UPGRADE_CMD = 'fwupdate-check --force &>>/var/log/fwupdate-check.log &'
UPGRADE_START_TIMEOUT = 10  # seconds


def get_status() -> str:
    return subprocess.check_output(STATUS_CMD, shell=True).decode().strip()


def get_latest() -> Dict[str, Any]:
    output = subprocess.check_output(LATEST_CMD, shell=True).decode().strip()
    lines = output.split('\n')
    latest = {}
    for line in lines:
        parts = line.split(':')
        if len(parts) != 2:
            continue

        k, v = parts
        k = k.strip().lower()
        v = v.strip()
        if k == 'beta':
            latest[k] = v == 'true'

        else:
            latest[k] = v

    return latest


def start_upgrade() -> None:
    logging.info('starting firmware upgrade')
    subprocess.check_call(UPGRADE_CMD, shell=True)

    for _ in range(UPGRADE_START_TIMEOUT):
        if get_status() != 'idle':
            return

        time.sleep(1)

    raise Exception('Timeout waiting for upgrade to start')
