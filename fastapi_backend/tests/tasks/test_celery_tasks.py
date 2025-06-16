import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

import httpx
import asyncio as _asyncio

from app.tasks import extract_metrics, calculate_revenue_mwh, fetch_price_usd
from app.models import ASIC
from sqlalchemy import select
from sqlalchemy.sql.selectable import Select


@pytest.mark.asyncio
async def test_extract_metrics():
    timestamp = 1_600_000_000
    blk = {
        'height': 10,
        'time': timestamp,
        'hash': 'blockhash',
        'tx': ['txid1'],
    }
    # Mock rpc methods
    rpc = AsyncMock()
    rpc.getblockhash.return_value = 'prevhash'
    rpc.getblock.return_value = {'time': timestamp - 600}
    rpc.getrawtransaction.return_value = {'vout': [{'value': 12.5}, {'value': 1.5}]}
    rpc.getnetworkhashps.return_value = 100.0

    data = await extract_metrics(rpc, blk)
    assert data['height'] == 10
    assert isinstance(data['timestamp'], datetime)
    # Subsidy for height 10 is 50 BTC
    assert data['subsidy'] == 50.0
    # Fees = total_out - subsidy = 14.0 - 50.0 = -36.0
    assert data['fees'] == pytest.approx(-36.0)
    assert data['hashrate'] == 100.0
    assert data['time_delta_s'] == pytest.approx(600.0)

@pytest.mark.asyncio
async def test_fetch_price_usd(monkeypatch):
    # Set timestamp to 30 minutes ago
    ts = datetime.now(timezone.utc) - timedelta(minutes=30)
    data = {'timestamp': ts}

    class DummyResp:
        def __init__(self, json_data):
            self._json = json_data
        def json(self):
            return self._json

    # Prepare ms in milliseconds to match code expectation
    ms_millis = int(ts.timestamp() * 1000)
    async def dummy_get(self, url):
        return DummyResp({'prices': [[ms_millis, 123.45]]})

    monkeypatch.setattr(httpx.AsyncClient, 'get', dummy_get)
    # Prevent real sleep
    monkeypatch.setattr(_asyncio, 'sleep', AsyncMock())

    result = await fetch_price_usd(data)
    assert result['price_usd'] == 123.45
    # price_timestamp should match the converted ms
    assert result['price_timestamp'] == datetime.fromtimestamp(ms_millis / 1000, tz=timezone.utc)

@pytest.mark.asyncio
async def test_calculate_revenue_mwh(monkeypatch):
    # Create fake ASIC record
    AsicObj = SimpleNamespace(id=1, asic_power=500_000, asic_hash_rate=10_000)
    # Mock DB execute for select: return a sync result with scalars().all()
    select_result = MagicMock()
    # scalars().all() returns a list with our AsicObj
    select_result.scalars.return_value.all.return_value = [AsicObj]

    db = AsyncMock()
    # When awaited, db.execute returns select_result
    db.execute.return_value = select_result
    db.commit = AsyncMock()

    # Prepare data
    data = {
        'height': 100,
        'timestamp': datetime.now(timezone.utc),
        'subsidy': 6.25,
        'fees': 0.1,
        'hashrate': 20_000,
        'price_usd': 200.0,
    }

    # Run revenue calculation
    await calculate_revenue_mwh(db, data)

    # Should select ASICs once
    assert any(isinstance(call.args[0], Select) for call in db.execute.call_args_list), \
           "Expected a select query for ASIC"

    # Should have committed once
    assert db.commit.call_count == 1

    # Should have inserted revenue values
    assert db.execute.call_count >= 2
