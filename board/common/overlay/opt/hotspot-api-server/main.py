#!/usr/bin/env python

import asyncio
import base64
import logging

from typing import Awaitable, Callable

from aiohttp import web

import logs
import miner
import pubkey
import settings
import system


router = web.RouteTableDef()


# def get_auth_hash() -> str:
#     to_hash = f'{get_rpi_sn()}:{get_pub_key_hex()}'
#     return hashlib.sha256(to_hash.encode()).hexdigest()


def handle_auth(
    func: Callable[[web.Request], Awaitable[web.Response]]
) -> Callable[[web.Request], Awaitable[web.Response]]:
    async def handler(request: web.Request) -> web.Response:
        try:
            auth = request.headers['Authorization']

        except KeyError:
            return web.json_response({'error': 'unauthorized'}, status=401)

        auth = auth.lower()
        if auth != get_auth_hash():
            return web.json_response({'error': 'unauthorized'}, status=401)

        return await func(request)

    return handler


@router.get('/summary')
async def summary(request: web.Request) -> web.Response:
    mem_used, mem_total = system.get_mem_info()
    storage_used, storage_total = system.get_storage_info()

    return web.json_response({
        'serial_number': system.get_rpi_sn(),
        'cpu_usage': system.get_cpu_usage(),
        'mem_used': mem_used,
        'mem_total': mem_total,
        'storage_used': storage_used,
        'storage_total': storage_total,
        'temperature': system.get_temperature(),
        'miner_height': miner.get_height(),
        'miner_listen_addr': miner.get_listen_addr(),
        'hotspot_name': pubkey.get_name(),
        'fw_version': system.get_fw_version(),
        'ecc_sn': pubkey.get_ecc_sn(),
        'address': pubkey.get_address(),
        'pub_key': pubkey.get_pub_key_hex(),
        'eth_mac': system.get_eth_mac(),
        'wlan_mac': system.get_wlan_mac(),
        'uptime': system.get_uptime()
    })


@router.post('/reboot')
@handle_auth
async def reboot(request: web.Request) -> web.Response:
    loop = asyncio.get_event_loop()
    loop.call_later(2, system.reboot)

    return web.json_response({'message': 'ok'})


@router.post('/logs/start')
@handle_auth
async def logs_start(request: web.Request) -> web.Response:
    logs.enable_logs_sending()
    return web.json_response({'message': 'ok'})


@router.post('/logs/stop')
@handle_auth
async def logs_stop(request: web.Request) -> web.Response:
    logs.disable_logs_sending()
    return web.json_response({'message': 'ok'})


def make_app() -> web.Application:
    app = web.Application()
    app.add_routes(router)

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
