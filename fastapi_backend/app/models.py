from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, Float, DateTime, Index, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from uuid import uuid4
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class BlockData(Base):
    __tablename__ = "block_data"

    # composite index on (block_timestamp, block_number)
    __table_args__ = (
        Index("idx_block_timestamp_number", "block_timestamp", "block_number"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    block_timestamp = Column(DateTime(timezone=True), nullable=False)
    block_number = Column(Integer, unique=True, nullable=False)
    block_subsidy = Column(Float, nullable=False)
    block_transaction_fees = Column(Float, nullable=False)
    network_hash_rate = Column(Float, nullable=False)


class ExchangeRate(Base):
    __tablename__ = "exchange_rate"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    block_number = Column(Integer, unique=True, index=True, nullable=False)
    exchange_rate = Column(Float, nullable=False)
    exchange_rate_timestamp = Column(DateTime(timezone=True), index=True, nullable=False)


class ASIC(Base):
    __tablename__ = "asic"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asic_slug = Column(String, index=True)
    asic_name = Column(String, nullable=False)
    asic_hash_rate = Column(Float, nullable=False)
    asic_power = Column(Float, nullable=False)

    mwh_revenues = relationship(
        "MWHRevenue",
        back_populates="asic",
        cascade="all, delete-orphan",
    )


class MWHRevenue(Base):
    __tablename__ = "mwh_revenue"

    # composite index on (mwh_revenue_timestamp, asic_id)
    __table_args__ = (
        Index("idx_mwh_revenue_timestamp_asic_id", "mwh_revenue_timestamp", "asic_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    asic_id = Column(UUID(as_uuid=True), ForeignKey("asic.id"), nullable=False)
    asic = relationship("ASIC", back_populates="mwh_revenues")
    mwh_btc_revenue = Column(Float, nullable=False)
    mwh_usd_revenue = Column(Float, nullable=False)
    mwh_revenue_timestamp = Column(DateTime(timezone=True), nullable=False)
    block_number = Column(Integer, index=True, nullable=False)
