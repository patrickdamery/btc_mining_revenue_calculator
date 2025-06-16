from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import ExchangeRate
from app.schemas import ExchangeRate as ExchangeRateSchema

router = APIRouter(tags=["exchange_rate"])


@router.get("/", response_model=list[ExchangeRateSchema])
async def read_exchange_rate(
    exchange_rate_timestamp_start: datetime,
    exchange_rate_timestamp_end: datetime,
    db: AsyncSession = Depends(get_async_session),
):
    result = await db.execute(
        select(ExchangeRate).filter(
            ExchangeRate.exchange_rate_timestamp >= exchange_rate_timestamp_start.replace(tzinfo=timezone.utc),
            ExchangeRate.exchange_rate_timestamp <= exchange_rate_timestamp_end.replace(tzinfo=timezone.utc),
        )
    )
    exchange_rates = result.scalars().all()
    return [ExchangeRateSchema.model_validate(exchange_rate) for exchange_rate in exchange_rates]

