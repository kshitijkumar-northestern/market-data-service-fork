from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: datetime
    provider: str

class PollRequest(BaseModel):
    symbols: List[str] = Field(..., min_length=1, max_length=10)
    interval: int = Field(60, ge=30, le=3600)
    provider: str = "yfinance"

class PollResponse(BaseModel):
    job_id: str
    status: str = "accepted"
    config: dict

class MovingAverageResponse(BaseModel):
    symbol: str
    period: int
    average_value: float
    timestamp: datetime

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    kafka: str
    redis: str
