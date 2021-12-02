
import logging
import os
import shutil

from typing import Any, Dict, List, Optional

import asyncsubprocess


SCAN_CMD = 'connmanctl scan wifi'
SERVICES_CMD = 'connmanctl services'
CONNECT_CMD = (
    'cd /tmp && '
    '(echo "agent on"; sleep 1; echo "connect {nid}"; sleep 1; echo "{psk}"; sleep 1) | '
    'script -q -e -c connmanctl &&'
    'rm -f typescript'
)
FORGET_CMD = 'connmanctl config {nid} --remove'
CURRENT_NID_CMD = 'connmanctl services | grep "*AO" | tr -s " " | rev | cut -d " " -f 1 | rev'
ROOT_DIR = '/var/lib/connman'


async def _list_services() -> Dict[str, Dict[str, Any]]:
    try:
        output = await asyncsubprocess.check_output(SERVICES_CMD)
    except Exception:
        return {}

    services = {}
    for line in output.split('\n'):
        if not line.strip():
            continue

        line = line[4:]  # skip *AOR
        parts = line.split(' wifi_')
        if len(parts) == 2:
            ssid = parts[0].strip()
            if not ssid:
                continue
            nid = f'wifi_{parts[1]}'
            services[nid] = {'ssid': ssid, 'type': 'wifi'}
        else:
            parts = line.split(' ethernet_')
            if len(parts) == 2:
                nid = f'ethernet_{parts[1]}'
                services[nid] = {'type': 'ethernet'}

    return services


async def get_current_network() -> Optional[Dict[str, str]]:
    nid = await asyncsubprocess.check_output(CURRENT_NID_CMD)
    services = await _list_services()
    return services.get(nid)


async def scan_wifi() -> List[str]:
    logging.debug('scanning for wi-fi networks')
    try:
        await asyncsubprocess.check_output(SCAN_CMD)
    except Exception:
        pass

    services = (await _list_services()).values()
    services = [s['ssid'] for s in services if s['type'] == 'wifi']
    logging.debug('got %d wi-fi networks', len(services))

    return services


async def connect_wifi(ssid: str, psk: str) -> None:
    logging.debug('connecting to "%s" wi-fi network', ssid)

    services = await _list_services()
    for n, s in services.items():
        if s['type'] == 'wifi' and s['ssid'] == ssid:
            nid = n
            break
    else:
        raise Exception(f'Wi-Fi network not found: "{ssid}"')

    await asyncsubprocess.check_call(CONNECT_CMD.format(nid=nid, psk=psk))


async def forget_wifi() -> None:
    logging.debug('forgetting current wi-fi network config')

    nid = await asyncsubprocess.check_output(CURRENT_NID_CMD)
    if not nid.startswith('wifi'):
        return

    await asyncsubprocess.check_output(FORGET_CMD.format(nid=nid))

    shutil.rmtree(os.path.join(ROOT_DIR, nid), ignore_errors=True)


async def has_ethernet() -> bool:
    services = await _list_services()
    for _, s in services.items():
        if s['type'] == 'ethernet':
            return True

    return False


async def connect_ethernet() -> None:
    logging.debug('connecting to ethernet')

    services = await _list_services()
    for n, s in services.items():
        if s['type'] == 'ethernet':
            await asyncsubprocess.check_call(CONNECT_CMD.format(nid=n))
            logging.debug('connected to ethernet')
            return

    raise Exception('Ethernet connection not available')
