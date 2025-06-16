from fastapi.routing import APIRoute
from app.schemas import BlockData, ExchangeRate


# helper functions
def walk_chain(seed, fetch, nxt):
    async def _gen():
        current = seed
        while current:
            blk = await fetch(current)
            yield blk
            current = nxt(blk)
    return _gen()

def amap(func, agen):
    async def _gen():
        async for item in agen:
            yield await func(item)
    return _gen()

def block_subsidy(height):
    halvings = height // 210_000
    if halvings >= 64:
        return 0.0
    sats = 50 * 100_000_000 >> halvings
    return sats / 100_000_000

def simple_generate_unique_route_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"