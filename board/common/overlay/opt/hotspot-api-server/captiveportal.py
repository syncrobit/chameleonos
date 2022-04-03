
import logging

import asyncsubprocess


CAPTIVE_PORTAL_STARTED_CMD = 'ps aux | grep /hostapd | grep -qv grep'
CAPTIVE_PORTAL_START_CMD = 'service hostapd start && service dnsmasq start'


async def is_started() -> bool:
    try:
        await asyncsubprocess.check_output(CAPTIVE_PORTAL_STARTED_CMD)
        return True
    except asyncsubprocess.StatusCodeError:
        return False


async def start() -> None:
    if await is_started():
        return

    logging.info('starting captive portal')
    await asyncsubprocess.check_output(CAPTIVE_PORTAL_START_CMD)
