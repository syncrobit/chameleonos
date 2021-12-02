
import asyncio

from typing import Awaitable


async def call_with_delay(awaitable: Awaitable, delay: float) -> None:
    await asyncio.sleep(delay)
    await awaitable
