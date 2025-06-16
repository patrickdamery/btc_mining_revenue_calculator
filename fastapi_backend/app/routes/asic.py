from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_async_session
from app.models import ASIC
from app.schemas import ASIC as ASICSchema

router = APIRouter(tags=["asic"])


@router.get("/", response_model=list[ASICSchema])
async def list_asics(
    db: AsyncSession = Depends(get_async_session),
):
    
    result = await db.execute(
        select(ASIC)
    )
    asics = result.scalars().all()
    return [ASICSchema.model_validate(asic) for asic in asics]

