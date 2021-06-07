#!/usr/bin/env python

import asyncio
import base64
import datetime
import logging
import os
import time

from typing import Awaitable, Callable

from aiohttp import web

import cpufreq
import gatewayconfig
import ledstrip
import logs
import miner
import pf
import pubkey
import sbapi
import settings
import system
import user


AUTH_REALM_PREFIX = 'SyncroB.it Chameleon'

router = web.RouteTableDef()


def make_auth_error_response() -> web.Response:
    www_authenticate = f'Basic realm="{AUTH_REALM_PREFIX} {system.get_rpi_sn()}"'
    return web.Response(status=401, headers={'WWW-Authenticate': www_authenticate})


def handle_auth(
    func: Callable[[web.Request], Awaitable[web.Response]]
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def handler(request: web.Request) -> web.Response:
        try:
            auth = request.headers['Authorization']

        except KeyError:
            return make_auth_error_response()

        try:
            unpw = base64.urlsafe_b64decode(auth[5:].strip()).decode()

        except (ValueError, TypeError):
            return make_auth_error_response()

        try:
            username, password = unpw.split(':')

        except ValueError:
            return make_auth_error_response()

        if not user.verify_credentials(username, password):
            logging.error(f'invalid credentials for %s', username)
            return make_auth_error_response()

        logging.debug(f'authentication successful for %s', username)

        return await func(request)

    return handler


@router.get('/summary')
async def get_summary(request: web.Request) -> web.Response:
    mem_used, mem_total = system.get_mem_info()
    storage_used, storage_total = system.get_storage_info()

    quick = request.query.get('quick') == 'true'

    summary = {
        'serial_number': system.get_rpi_sn(),
        'cpu_usage': system.get_cpu_usage(),
        'mem_used': mem_used,
        'mem_total': mem_total,
        'storage_used': storage_used,
        'storage_total': storage_total,
        'temperature': system.get_temperature(),
        'miner_height': miner.get_height() if not quick else None,
        'miner_listen_addr': miner.get_listen_addr() if not quick else None,
        'hotspot_name': pubkey.get_name(),
        'concentrator_model': pf.get_concentrator_model() if not quick else None,
        'region': miner.get_region() if not quick else None,
        'fw_version': system.get_fw_version(),
        'ecc_sn': pubkey.get_ecc_sn(),
        'swarm_key_mode': miner.is_swarm_key_mode(),
        'address': pubkey.get_address(),
        'pub_key': pubkey.get_pub_key_hex(),
        'eth_mac': system.get_eth_mac(),
        'wlan_mac': system.get_wlan_mac(),
        'uptime': system.get_uptime(),
        'time': int(time.time())
    }

    if request.query.get('pretty') == 'true':
        blockchain_height = await miner.get_blockchain_height()
        lag = blockchain_height - (summary['miner_height'] or 0)

        summary['Serial Number'] = summary.pop('serial_number')
        summary['CPU Usage'] = f"{summary.pop('cpu_usage')} %"
        summary['Memory Usage'] = f"{summary.pop('mem_used')}/{summary.pop('mem_total')} MB"
        summary['Storage Usage'] = f"{summary.pop('storage_used')}/{summary.pop('storage_total')} MB"
        summary['Temperature'] = f"{summary.pop('temperature')} C"
        summary['Miner Height'] = f"{summary.pop('miner_height')}/{blockchain_height} (lag is {lag})"
        summary['Miner Listen Address'] = summary.pop('miner_listen_addr')
        summary['Hotspot Name'] = summary.pop('hotspot_name')
        summary['Concentrator Model'] = summary.pop('concentrator_model')
        summary['Region'] = summary.pop('region')
        summary['Firmware Version'] = summary.pop('fw_version')
        summary['ECC Serial Number'] = summary.pop('ecc_sn')
        summary['Swarm Key Mode'] = summary.pop('swarm_key_mode')
        summary['Address'] = summary.pop('address')
        summary['Public Key'] = summary.pop('pub_key')
        summary['Ethernet MAC'] = summary.pop('eth_mac')
        summary['Wi-Fi MAC'] = summary.pop('wlan_mac')
        summary['Uptime'] = str(datetime.timedelta(seconds=summary.pop('uptime')))
        summary['Date/Time'] = f"{str(datetime.datetime.utcfromtimestamp(summary.pop('time')))} (UTC)"

    return web.json_response(summary)


@router.get('/nettest')
async def get_net_test(request: web.Request) -> web.Response:
    net_test = system.net_test()
    return web.json_response(net_test)


@router.get('/stats')
async def get_stats(request: web.Request) -> web.Response:
    stats = await sbapi.get_stats(pubkey.get_address())
    return web.json_response(stats)


@router.get('/config')
@handle_auth
async def get_config(request: web.Request) -> web.Response:
    cpu_freq_config = cpufreq.get_config()
    led_strip_config = ledstrip.get_config()
    nat_config = miner.get_nat_config()
    pf_config = pf.get_config()
    return web.json_response({
        'cpu_freq_max': cpu_freq_config['max'],
        'led_brightness': led_strip_config['brightness'],
        'led_ok_color': led_strip_config['ok_color'],
        'nat_external_ip': nat_config['external_ip'],
        'nat_external_port': nat_config['external_port'],
        'nat_internal_port': nat_config['internal_port'],
        'pf_antenna_gain': pf_config['antenna_gain'],
        'pf_rssi_offset': pf_config['rssi_offset'],
        'pf_tx_power': pf_config['tx_power']
    })


@router.patch('/config')
@handle_auth
async def set_config(request: web.Request) -> web.Response:
    config = await request.json()
    restart_miner = False
    restart_pf = False

    cpu_freq_config = {}
    for field in ('max',):
        if f'cpu_freq_{field}' in config:
            cpu_freq_config[field] = config[f'cpu_freq_{field}']

    if cpu_freq_config:
        cpufreq.set_config(cpu_freq_config)
        cpufreq.restart()

    led_strip_config = {}
    for field in ('brightness', 'ok_color'):
        if f'led_{field}' in config:
            led_strip_config[field] = config[f'led_{field}']

    if led_strip_config:
        ledstrip.set_config(led_strip_config)
        ledstrip.restart()

    nat_config = {}
    for field in ('external_ip', 'external_port', 'internal_port'):
        if f'nat_{field}' in config:
            nat_config[field] = config[f'nat_{field}']

    if nat_config:
        miner.set_nat_config(nat_config)
        restart_miner = True

    pf_config = {}
    for field in ('antenna_gain', 'rssi_offset', 'tx_power'):
        if f'pf_{field}' in config:
            pf_config[field] = config[f'pf_{field}']

    if pf_config:
        pf.set_config(pf_config)
        restart_pf = True

    if 'password' in config:
        user.set_password(user.DEFAULT_USERNAME, config['password'])

    if restart_miner:
        miner.restart()
    if restart_pf:
        pf.restart()

    return web.Response(status=204)


@router.post('/reboot')
@handle_auth
async def reboot(request: web.Request) -> web.Response:
    loop = asyncio.get_event_loop()
    loop.call_later(2, system.reboot)

    return web.Response(status=204)


@router.post('/pair')
@handle_auth
async def pair(request: web.Request) -> web.Response:
    gatewayconfig.enable_pair()

    return web.Response(status=204)


@router.post('/resync')
@handle_auth
async def resync(request: web.Request) -> web.Response:
    miner.resync()
    miner.restart()

    return web.Response(status=204)


@router.post('/logs/start')
@handle_auth
async def logs_start(request: web.Request) -> web.Response:
    logs.enable_logs_sending()

    return web.Response(status=204)


@router.post('/logs/stop')
@handle_auth
async def logs_stop(request: web.Request) -> web.Response:
    logs.disable_logs_sending()

    return web.Response(status=204)


@router.get(r'/{path:[a-zA-Z0-9_/-]+}')
@handle_auth
async def html_page(request: web.Request) -> web.FileResponse:
    path = f'{request.match_info["path"]}.html'
    full_path = os.path.join(settings.HTML_PATH, path)
    if not os.path.exists(full_path):
        raise web.HTTPNotFound()

    return web.FileResponse(full_path)


@router.get('/')
@handle_auth
async def html_index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(os.path.join(settings.HTML_PATH, 'index.html'))


def make_app() -> web.Application:
    app = web.Application()
    app.add_routes(router)
    app.add_routes([web.static('/resources', settings.RESOURCES_PATH)])

    return app


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s [%(levelname)s]: %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    logging.info('hello!')

    app = make_app()
    web.run_app(app, port=settings.PORT, print=lambda *args: None)
