import json
import logging

from typing import Any

import aiohttp

from aiohttp import hdrs

import asyncsubprocess


HELIUM_API_CONF = '/var/run/helium-api.conf'
DEFAULT_TIMEOUT = 60

base_url = None


async def api_request(
    method: str,
    path: str,
    body: Any = None,
    timeout: int = DEFAULT_TIMEOUT,
    use_json: bool = True
) -> Any:
    global base_url

    if base_url is None:
        cmd = f'source {HELIUM_API_CONF} && echo ${{BASE_URL}}'
        base_url = await asyncsubprocess.check_output(cmd)
        logging.debug('using Helium API base URL = "%s"', base_url)

    url = f'{base_url}{path}/'
    headers = {}
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


async def is_reachable() -> bool:
    try:
        response = await api_request('GET', '/stats', timeout=10)
    except Exception:
        return False

    return 'data' in response
