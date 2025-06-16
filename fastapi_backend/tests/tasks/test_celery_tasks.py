import pytest
import asyncio
from datetime import datetime, timezone, timedelta

import httpx

# Import functions to test
from app.tasks import block_subsidy, fetch_price_usd, walk_chain, amap

# ---------- Tests for block_subsidy ----------
@pytest.mark.parametrize("height,expected", [
    (0, 50.0),       # genesis
    (210000, 25.0),  # first halving
    (420000, 12.5),  # second halving
    (210000*64, 0.0) # subsidy zero after 64 halving
])
def test_block_subsidy(height, expected):
    assert block_subsidy(height) == expected

# ---------- Tests for walk_chain and amap ----------

async def dummy_fetch(hash_):
    # pretend blocks are dicts with "hash" and "next" appended
    return {"hash": hash_, "next": str(int(hash_) + 1) if int(hash_) < 3 else None}

def dummy_next(block):
    return block.get("next")

async def dummy_extract(block):
    # return just the block value
    return int(block["hash"]) * 2

@pytest.mark.asyncio
async def test_walk_chain_and_amap():
    # Walk from '1' through '2','3'
    chain = walk_chain("1", dummy_fetch, dummy_next)
    result = []
    async for blk in chain:
        result.append(blk)
    # Expect three blocks
    assert [b["hash"] for b in result] == ["1", "2", "3"]

    # Test amap: double values
    chain = walk_chain("1", dummy_fetch, dummy_next)
    mapped = amap(dummy_extract, chain)
    collected = []
    async for val in mapped:
        collected.append(val)
    assert collected == [2, 4, 6]

# ---------- Tests for fetch_price_usd ----------

class DummyResponse:
    def __init__(self, json_data):
        self._json = json_data
    def json(self):
        return self._json

class DummyClient:
    def __init__(self, response):
        self.response = response
    async def __aenter__(self): return self
n    async def __aexit__(self, exc_type, exc, tb): pass
    async def get(self, url):
        return self.response

@pytest.mark.asyncio
async def test_fetch_price_usd(monkeypatch):
    # Prepare a fake data dict
    ts = datetime.now(timezone.utc) - timedelta(hours=1)
    data = {"timestamp": ts}
    # Simulate hourly granularity: one price point
    ms = int(ts.timestamp() * 1000)
    fake_prices = {"prices": [[ms, 12345.67]]}
    dummy_resp = DummyResponse(fake_prices)
    # Monkeypatch httpx.AsyncClient
    monkeypatch.setattr(httpx, "AsyncClient", lambda: DummyClient(dummy_resp))
    # Call the function
    enriched = await fetch_price_usd(data.copy())
    assert enriched["price_usd"] == 12345.67
    assert enriched["price_timestamp"] == datetime.fromtimestamp(ms/1000, tz=timezone.utc)

    # Test no prices case
    dummy_resp_empty = DummyResponse({"prices": []})
    monkeypatch.setattr(httpx, "AsyncClient", lambda: DummyClient(dummy_resp_empty))
    enriched_empty = await fetch_price_usd(data.copy())
    assert enriched_empty["price_usd"] is None
    assert enriched_empty["price_timestamp"] is None
