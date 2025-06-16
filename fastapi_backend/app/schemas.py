from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime


class BlockData(BaseModel):
    id: UUID
    block_timestamp: datetime
    block_number: int
    block_subsidy: float
    block_transaction_fees: float
    network_hash_rate: float

    model_config = ConfigDict(frozen=True, from_attributes=True)


class ExchangeRate(BaseModel):
    id: UUID
    block_number: int
    exchange_rate: float
    exchange_rate_timestamp: datetime

    model_config = ConfigDict(frozen=True, from_attributes=True)


class ASIC(BaseModel):
    id: UUID
    asic_slug: str
    asic_name: str
    asic_hash_rate: float
    asic_power: float

    model_config = ConfigDict(frozen=True, from_attributes=True)


class MWHRevenue(BaseModel):
    id: UUID
    asic_id: UUID
    mwh_btc_revenue: float
    mwh_usd_revenue: float
    mwh_revenue_timestamp: datetime
    block_number: int

    model_config = ConfigDict(frozen=True, from_attributes=True)
