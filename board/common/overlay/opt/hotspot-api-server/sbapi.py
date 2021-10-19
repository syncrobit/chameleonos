import asyncio
import json
import re

from typing import Any, Dict, Optional

import aiohttp

from aiohttp import hdrs, web


BASE_URL = 'https://api.syncrob.it'
AUTH_TOKEN = '3F4ECC8F2C95134BCA7281C83B879'
LISTEN_ADDR_IPV4_RE = re.compile(r'^/ip4/([0-9.]{7,15})/tcp/(\d+)$')
DEFAULT_TIMEOUT = 60


async def api_request(
    method: str,
    path: str,
    body: Any = None,
    timeout: int = DEFAULT_TIMEOUT,
    use_json: bool = True
) -> Any:
    url = f'{BASE_URL}{path}/'
    headers = {
        'Authorization': AUTH_TOKEN
    }
    if body:
        headers['Content-Type'] = 'application/json'

    # The aiohttp lib removes the Authorization header upon any kind of redirect. We use this hack prevent it from
    # identifying the Authorization header at all.
    auth_header_name = hdrs.AUTHORIZATION
    hdrs.AUTHORIZATION = 'workaround_for_redirect'
    try:
        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(timeout)) as client:
            if use_json:
                ctx = client.request(method=method, url=url, json=body)
            else:
                ctx = client.request(method=method, url=url, data=body)

            async with ctx as response:
                if use_json:
                    return json.loads(await response.text())
                else:
                    return response.headers, await response.text()
    finally:
        hdrs.AUTHORIZATION = auth_header_name


async def get_stats(address: str) -> Dict[str, Any]:
    stats = await api_request('POST', '/stats', body={'gw_addr': address})
    for k, v in stats.items():
        if k.startswith('rewards_') or k.endswith('_price'):
            stats[k] = float(v)

    return stats


async def get_activity(address: str) -> Dict[str, Any]:
    return await api_request('POST', '/activity', body={'gw_addr': address})


async def test_listen_addr(listen_addr: str) -> Optional[bool]:
    m = LISTEN_ADDR_IPV4_RE.match(listen_addr)
    if not m:
        return

    ip, port = m.groups()
    port = int(port)
    body = {
        'ip_address': ip,
        'port': port
    }
    try:
        response = await api_request('POST', '/minerlistencheck', body=body, timeout=12)
    except (asyncio.TimeoutError, json.decoder.JSONDecodeError):
        return

    try:
        return response['status'] == 'Port open'
    except:
        return False


async def passthrough(request: web.Request) -> web.Response:
    path = request.path[6:]  # skip /sbapi
    timeout = request.query.get('timeout')
    if timeout:
        timeout = int(timeout)

    request_body = await request.read()
    headers, response_body = await api_request(request.method, path, request_body, timeout=timeout, use_json=False)

    return web.Response(
        content_type=headers.get('Content-Type', 'text/plain').split()[0],
        body=response_body
    )
