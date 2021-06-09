
import aiohttp.hdrs
import json

from typing import Any, Dict


BASE_URL = 'https://api.syncrob.it'
AUTH_TOKEN = '3F4ECC8F2C95134BCA7281C83B879'


async def api_request(method: str, path: str, body: Any = None) -> Any:
    url = f'{BASE_URL}{path}/'
    headers = {
        'Authorization': AUTH_TOKEN
    }
    if body:
        headers['Content-Type'] = 'application/json'

    # The aiohttp lib removes the Authorization header upon any kind of redirect. We use this hack prevent it from
    # identifying the Authorization header at all.
    auth_header_name = aiohttp.hdrs.AUTHORIZATION
    aiohttp.hdrs.AUTHORIZATION = 'workaround_for_redirect'
    try:
        async with aiohttp.ClientSession(headers=headers) as client:
            async with client.request(method=method, url=url, json=body) as response:
                return json.loads(await response.text())

    finally:
        aiohttp.hdrs.AUTHORIZATION = auth_header_name


async def get_stats(address: str) -> Dict[str, Any]:
    stats = await api_request('POST', '/stats', body={'gw_addr': address})
    for k, v in stats.items():
        if k.startswith('rewards_') or k.endswith('_price'):
            stats[k] = float(v)

    return stats


async def get_activity(address: str) -> Dict[str, Any]:
    return await api_request('POST', '/activity', body={'gw_addr': address})
