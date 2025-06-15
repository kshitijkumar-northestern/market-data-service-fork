from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.schemas.market_data import PriceResponse, PollRequest, PollResponse
from app.services.market_service import MarketService
from app.api.dependencies import get_market_service

router = APIRouter()

@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(
    symbol: str = Query(..., description="Stock symbol (e.g., AAPL)"),
    provider: Optional[str] = Query("yfinance", description="Data provider"),
    market_service: MarketService = Depends(get_market_service)
):
    """Get latest price for a symbol"""
    try:
        price_data = await market_service.get_latest_price(symbol, provider)
        return PriceResponse(**price_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/poll", response_model=PollResponse, status_code=202)
async def create_polling_job(
    poll_request: PollRequest,
    market_service: MarketService = Depends(get_market_service)
):
    """Create a polling job for multiple symbols"""
    try:
        job_data = market_service.create_polling_job(
            symbols=poll_request.symbols,
            interval=poll_request.interval,
            provider=poll_request.provider
        )
        return PollResponse(**job_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from app.schemas.market_data import PriceResponse, PollRequest, PollResponse
from app.services.market_service import MarketService
from app.api.dependencies import get_market_service

router = APIRouter()

@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(
    symbol: str = Query(..., description="Stock symbol (e.g., AAPL)"),
    provider: Optional[str] = Query("yfinance", description="Data provider"),
    market_service: MarketService = Depends(get_market_service)
):
    """Get latest price for a symbol"""
    try:
        price_data = await market_service.get_latest_price(symbol, provider)
        return PriceResponse(**price_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/poll", response_model=PollResponse, status_code=202)
async def create_polling_job(
    poll_request: PollRequest,
    market_service: MarketService = Depends(get_market_service)
):
    """Create a polling job for multiple symbols"""
    try:
        job_data = market_service.create_polling_job(
            symbols=poll_request.symbols,
            interval=poll_request.interval,
            provider=poll_request.provider
        )
        return PollResponse(**job_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")