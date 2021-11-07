import json

from typing import Any

import aiohttp

from aiohttp import hdrs


BASE_URL = 'https://api.helium.io/v1'
DEFAULT_TIMEOUT = 60


async def api_request(
    method: str,
    path: str,
    body: Any = None,
    timeout: int = DEFAULT_TIMEOUT,
    use_json: bool = True
) -> Any:
    url = f'{BASE_URL}{path}/'
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


async def get_blockchain_height() -> int:
    result = await api_request('GET', '/blocks/height')
    return result['data']['height']
