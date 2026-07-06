import asyncio
from .config import get_settings

config = get_settings()

gen_semaphore = asyncio.Semaphore(config.GENERATION_SEMAPHORE_SIZE)

async def with_gen_semaphore(coro):
    async with gen_semaphore:
        return await coro