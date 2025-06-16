from app.models import BlockData, ExchangeRate, MWHRevenue, ASIC
from sqlalchemy import and_
from sqlalchemy.future import select
from datetime import timezone


async def fetch_block_data_with_exchange_rate(db, timestamp_start, timestamp_end):
    stmt = (
        select(BlockData, ExchangeRate)
        .join(
            ExchangeRate,
            ExchangeRate.block_number == BlockData.block_number
        )
        .where(
            and_(
                BlockData.block_timestamp >= timestamp_start.replace(tzinfo=timezone.utc),
                BlockData.block_timestamp <= timestamp_end.replace(tzinfo=timezone.utc),
            )
        )
        .order_by(BlockData.block_timestamp)
    )

    result = await db.execute(stmt)
    rows = result.all()
    return rows


async def fetch_mwh_revenue(db, timestamp_start, timestamp_end, asic_id):
    asic = await db.execute(
        select(ASIC)
        .where(
            ASIC.id == asic_id
        )
    )
    asic = asic.scalars().first()

    stmt = (
        select(MWHRevenue)
        .where(
            and_(
                MWHRevenue.mwh_revenue_timestamp >= timestamp_start.replace(tzinfo=timezone.utc),
                MWHRevenue.mwh_revenue_timestamp <= timestamp_end.replace(tzinfo=timezone.utc),
                MWHRevenue.asic_id == asic.id
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()