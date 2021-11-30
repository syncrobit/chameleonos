
import logging
import os

import asyncsubprocess


MASK_FILE = '/data/etc/no_S55openvpn'
START_CMD = 'service openvpn restart'
STOP_CMD = 'service openvpn stop'


def is_enabled() -> bool:
    return not os.path.exists(MASK_FILE)


async def set_enabled(enabled: bool) -> None:
    logging.info('%s remote access', ['disabling', 'enabling'][enabled])

    if enabled:
        if os.path.exists(MASK_FILE):
            os.remove(MASK_FILE)

        await asyncsubprocess.check_call(START_CMD)

    else:
        if not os.path.exists(MASK_FILE):
            with open(MASK_FILE, 'w'):
                pass

        await asyncsubprocess.check_call(STOP_CMD)
