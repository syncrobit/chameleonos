
import logging
import time

from typing import Any, Dict

import asyncsubprocess


STATUS_CMD = 'fwupdate status'
LATEST_CMD = 'fwupdate-check --info'
UPGRADE_CMD = 'fwupdate-check --force &>>/var/log/fwupdate-check.log &'
UPGRADE_START_TIMEOUT = 10  # seconds


async def get_status() -> str:
    status = await asyncsubprocess.check_output(STATUS_CMD)
    status = status.replace('[custom]', '').strip()

    return status


async def get_latest() -> Dict[str, Any]:
    output = await asyncsubprocess.check_output(LATEST_CMD)
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


async def start_upgrade() -> None:
    logging.info('starting firmware upgrade')
    await asyncsubprocess.check_call(UPGRADE_CMD)

    for _ in range(UPGRADE_START_TIMEOUT):
        if await get_status() != 'idle':
            return

        time.sleep(1)

    raise Exception('Timeout waiting for upgrade to start')
