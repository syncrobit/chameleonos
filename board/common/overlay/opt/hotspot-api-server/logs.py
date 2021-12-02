
import logging
import os

from typing import Optional

import asyncsubprocess


SEND_LOGS_ACTIVE_FILE = '/var/run/send_logs_active'
LOG_TAIL_CMD = 'tail -n {max_lines} {file_path} | tac'
DEF_MAX_LINES = 1000

LOG_FILES = {
    'miner': '/var/log/miner/console.log',
    'packet_forwarder': '/var/log/packet_forwarder.log',
    'kernel': '/var/log/dmesg.log',
    'system': '/var/log/messages'
}


def enable_logs_sending() -> None:
    logging.info('enabling logs sending')
    with open(SEND_LOGS_ACTIVE_FILE, 'w'):
        pass


def disable_logs_sending() -> None:
    logging.info('disabling logs sending')
    try:
        os.remove(SEND_LOGS_ACTIVE_FILE)

    except IOError:
        pass


async def get_log(name: str, max_lines: Optional[int] = None) -> Optional[str]:
    file_path = LOG_FILES.get(name)
    if not file_path:
        return
    if max_lines is None:
        max_lines = DEF_MAX_LINES

    cmd = LOG_TAIL_CMD.format(max_lines=max_lines, file_path=file_path)
    return await asyncsubprocess.check_output(cmd)
