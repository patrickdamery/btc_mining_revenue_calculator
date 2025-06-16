from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import BlockData
from app.schemas import BlockData as BlockDataSchema

router = APIRouter(tags=["block_data"])


@router.get("/", response_model=list[BlockDataSchema])
async def read_block_data(
    block_timestamp_start: datetime,
    block_timestamp_end: datetime,
    db: AsyncSession = Depends(get_async_session),
):
    
    result = await db.execute(
        select(BlockData).filter(
            BlockData.block_timestamp >= block_timestamp_start.replace(tzinfo=timezone.utc),
            BlockData.block_timestamp <= block_timestamp_end.replace(tzinfo=timezone.utc),
        )
    )
    blocks = result.scalars().all()
    return [BlockDataSchema.model_validate(block) for block in blocks]

