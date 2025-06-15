from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .database import Base


class RawMarketResponse(Base):
    __tablename__ = "raw_market_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    provider = Column(String(50), nullable=False)
    raw_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_raw_symbol_timestamp", "symbol", "timestamp"),)


class PricePoint(Base):
    __tablename__ = "price_points"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    provider = Column(String(50), nullable=False)
    raw_response_id = Column(UUID(as_uuid=True), nullable=True)

    __table_args__ = (Index("idx_price_symbol_timestamp", "symbol", "timestamp"),)


class MovingAverage(Base):
    __tablename__ = "moving_averages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    period = Column(Integer, nullable=False, default=5)
    average_value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("idx_ma_symbol_timestamp", "symbol", "timestamp"),)


class PollingJob(Base):
    __tablename__ = "polling_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(100), unique=True, nullable=False)
    symbols = Column(Text, nullable=False)
    interval = Column(Integer, nullable=False)
    provider = Column(String(50), nullable=False)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_run = Column(DateTime, nullable=True)
