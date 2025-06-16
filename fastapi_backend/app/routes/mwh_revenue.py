from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.schemas import MWHRevenue
from app.crud import fetch_mwh_revenue

router = APIRouter(tags=["mwh_revenue"])


@router.get("/", response_model=list[MWHRevenue])
async def get_mwh_revenue(
    timestamp_start: datetime,
    timestamp_end: datetime,
    asic_id: str,
    db: AsyncSession = Depends(get_async_session),
):
    mwh_revenue = await fetch_mwh_revenue(
        db,
        timestamp_start,
        timestamp_end,
        asic_id
    )
    return [MWHRevenue.model_validate(p) for p in mwh_revenue]
