import os
import asyncio
from urllib.parse import urlparse
from datetime import datetime, timezone
from functools import reduce

import httpx
from bitcoinrpc import BitcoinRPC

from .celery_app import celery_app
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, insert

from .models import BlockData, ExchangeRate, ASIC, MWHRevenue
from .config import settings
from .utils import block_subsidy, amap, walk_chain
import logging
logger = logging.getLogger(__name__)


# constants
START_HEIGHT = int(settings.START_BLOCK_HEIGHT)
RPC_URL      = settings.BTC_NODE_RPC_URL


# Extract block metrics
async def extract_metrics(rpc, blk):
    h  = blk["height"]
    ts = datetime.fromtimestamp(blk["time"], tz=timezone.utc)
    sub = block_subsidy(h)

    # Get previous block so we can calculate the time delta.
    prev_hash = await rpc.getblockhash(h - 1)
    prev_blk = await rpc.getblock(prev_hash, 1)
    prev_blk_ts = datetime.fromtimestamp(prev_blk["time"], tz=timezone.utc)
    time_delta = ts - prev_blk_ts

    # coinbase tx contains what miner received → subsidy + fees
    coinbase = await rpc.getrawtransaction(blk["tx"][0], True, blk["hash"])
    outs = list(map(lambda v: v.get("value", 0.0), coinbase.get("vout", [])))
    total_out = reduce(lambda a, b: a + b, outs, 0.0)
    fees      = total_out - sub

    # get network hashrate at block height since last difficulty adjustment.
    nh = await rpc.getnetworkhashps(height=h)
    return {
        "height": h,
        "timestamp": ts,
        "subsidy": sub,
        "fees": fees,
        "hashrate": nh,
        "time_delta_s": time_delta.total_seconds(),
    }

async def calculate_revenue_mwh(db, data):
    # get all available asic entries
    asics = await db.execute(
        select(ASIC)
    )
    asics = asics.scalars().all()

    for asic in asics:
        # Determine how many ASICs we need to consume 1MWh of energy.
        # 1MWh = 1000000 Wh
        number_of_asics = 1000000 / asic.asic_power    
        total_hashrate = asic.asic_hash_rate * number_of_asics
        # rpc server returns average per second network hashrate, we've calculated our total hashrate per second
        # so we can just divide total_hashrate by network_hashrate (+ our extra hashrate) to get our share of the network.
        # See: https://developer.bitcoin.org/reference/rpc/getnetworkhashps.html?highlight=getnetworkhashps
        share_of_hashrate = total_hashrate / (data["hashrate"] + total_hashrate)
        block_revenue = float(data["subsidy"]) + float(data["fees"])
        share_of_revenue = block_revenue * share_of_hashrate
        share_of_revenue_usd = share_of_revenue * data["price_usd"]
        logger.info(f"block_revenue: {block_revenue}, number of asics: {number_of_asics}, total_hashrate: {total_hashrate}, share_of_hashrate: {share_of_hashrate}, share_of_revenue: {share_of_revenue}, share_of_revenue_usd: {share_of_revenue_usd}")

        # write mwh revenue
        await db.execute(
            insert(MWHRevenue).values(
                block_number=data["height"],
                asic_id=asic.id,
                mwh_btc_revenue=share_of_revenue,
                mwh_usd_revenue=share_of_revenue_usd,
                mwh_revenue_timestamp=data["timestamp"],
            )
        )
        await db.commit()

# Add USD price
async def fetch_price_usd(data):
    ts       = data["timestamp"]
    now      = datetime.now(timezone.utc)
    age_secs = (now - ts).total_seconds()

    # CG has changing granularity the further back in time we go on public api,
    # Choose a half-window (in seconds) to match CG granularity:
    # 0–1 day   → 5 min intervals → ±300 s
    # 1–90 days → hourly        → ±3 600 s (1 h)
    # 90–365 days → daily       → ±86 400 s (1 d)
    # >365 days  → use daily too (but data may be missing)
    if age_secs <= 86400:
        half_window = 300
    elif age_secs <= 90 * 86400:
        half_window = 3600
    else:
        half_window = 86400

    center = int(ts.timestamp())
    frm    = center - half_window
    to     = center + half_window

    url = (
        "https://api.coingecko.com/api/v3/coins/bitcoin"
        f"/market_chart/range?vs_currency=usd&from={frm}&to={to}"
    )
    async with httpx.AsyncClient() as client:
        resp   = await client.get(url)
        prices = resp.json().get("prices", [])

    # throttle to ~5 calls/minute
    await asyncio.sleep(12)

    if not prices:
        return {
            **data,
            "price_usd": None,
            "price_timestamp": None,
        }

    # pick the datapoint closest in time
    ms, price = min(
        prices,
        key=lambda p: abs((p[0] / 1000) - ts.timestamp())
    )
    return {
        **data,
        "price_usd": price,
        "price_timestamp": datetime.fromtimestamp(ms / 1000, tz=timezone.utc),
    }

async def _run_pipeline():
    # setup DB
    parsed_db_url = urlparse(settings.DATABASE_URL)

    async_db_connection_url = (
        f"postgresql+asyncpg://{parsed_db_url.username}:{parsed_db_url.password}@"
        f"{parsed_db_url.hostname}{':' + str(parsed_db_url.port) if parsed_db_url.port else ''}"
        f"{parsed_db_url.path}"
    )

    engine = create_async_engine(async_db_connection_url, future=True)
    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )

    # Setup RPC + DB session
    async with BitcoinRPC.from_config(RPC_URL, (
        os.getenv("BTC_NODE_USER"),
        os.getenv("BTC_NODE_PASS"),
    )) as rpc, AsyncSessionLocal() as db:

        # find starting point
        result = await db.execute(
            select(BlockData.block_number)
            .order_by(BlockData.block_number.desc())
            .limit(1)
        )
        last = result.scalars().first()
        tip_height = await rpc.getblockcount()
        if last is None:
            # first run, we could make a full backfill but for demo purposes we can specify a recent block.
            start_hash = await rpc.getblockhash(START_HEIGHT)
        else:
            # get hash of next block
            if last + 1 > tip_height:
                return
            
            start_hash = await rpc.getblockhash(last + 1)

        # build and run pipeline
        async def fetch_block(h): return await rpc.getblock(h, 1)
        def next_hash_of(blk): return blk.get("nextblockhash")

        chain     = walk_chain(start_hash, fetch_block, next_hash_of)
        metrics   = amap(lambda b: extract_metrics(rpc, b), chain)
        enriched  = amap(fetch_price_usd,   metrics)

        async for rec in enriched:
            # write block_data
            await db.execute(
                insert(BlockData).values(
                    block_number=rec["height"],
                    block_timestamp=rec["timestamp"],
                    block_subsidy=rec["subsidy"],
                    block_transaction_fees=rec["fees"],
                    network_hash_rate=rec["hashrate"],
                )
            )
            # write exchange_rate
            await db.execute(
                insert(ExchangeRate).values(
                    block_number=rec["height"],
                    exchange_rate=rec["price_usd"],
                    exchange_rate_timestamp=rec["price_timestamp"],
                )
            )
            await db.commit()

            # Compute and write mwh revenue for each asic
            await calculate_revenue_mwh(db, rec)

@celery_app.task(name="app.tasks.fetch_and_store_all")
def fetch_and_store_all():
    asyncio.run(_run_pipeline())
