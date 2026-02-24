"""
Currency API routes - Multi-currency support and conversion
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.services.currency_service import get_currency_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/currency", tags=["currency"])

# Request/Response models
class ConversionRequest(BaseModel):
    amount: float
    from_currency: str
    to_currency: str

class ConversionResponse(BaseModel):
    original_amount: float
    original_currency: str
    converted_amount: float
    target_currency: str
    exchange_rate: float
    currency_symbol: str
    formatted_amount: str
    conversion_timestamp: str

class RegionalPriceRequest(BaseModel):
    base_price_usd: float
    region: str
    target_currency: str

class CurrencyInfo(BaseModel):
    code: str
    symbol: str
    name: str
    decimal_places: int

@router.get("/supported", response_model=List[CurrencyInfo])
async def get_supported_currencies():
    """Get list of supported currencies"""
    try:
        currency_service = get_currency_service()
        currencies = currency_service.get_supported_currencies()
        
        return [
            CurrencyInfo(
                code=code,
                symbol=info['symbol'],
                name=info['name'],
                decimal_places=info['decimal_places']
            )
            for code, info in currencies.items()
        ]
    
    except Exception as e:
        logger.error(f"Failed to get supported currencies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get supported currencies")

@router.post("/convert", response_model=ConversionResponse)
async def convert_currency(request: ConversionRequest):
    """Convert amount between currencies"""
    try:
        currency_service = get_currency_service()
        
        result = currency_service.convert_amount(
            amount=request.amount,
            from_currency=request.from_currency.upper(),
            to_currency=request.to_currency.upper()
        )
        
        return ConversionResponse(**result)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Currency conversion failed: {e}")
        raise HTTPException(status_code=500, detail="Currency conversion failed")

@router.get("/exchange-rate/{from_currency}/{to_currency}")
async def get_exchange_rate(from_currency: str, to_currency: str):
    """Get exchange rate between two currencies"""
    try:
        currency_service = get_currency_service()
        
        rate = currency_service.get_exchange_rate(
            from_currency.upper(),
            to_currency.upper()
        )
        
        return {
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "exchange_rate": rate,
            "timestamp": currency_service.last_update.isoformat() if currency_service.last_update else None
        }
    
    except Exception as e:
        logger.error(f"Failed to get exchange rate: {e}")
        raise HTTPException(status_code=500, detail="Failed to get exchange rate")

@router.post("/regional-price")
async def get_regional_price(request: RegionalPriceRequest):
    """Get regionally adjusted price in target currency"""
    try:
        currency_service = get_currency_service()
        
        result = currency_service.get_regional_price(
            base_price_usd=request.base_price_usd,
            region=request.region.upper(),
            target_currency=request.target_currency.upper()
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Regional price calculation failed: {e}")
        raise HTTPException(status_code=500, detail="Regional price calculation failed")

@router.get("/trends/{currency}")
async def get_currency_trends(currency: str, days: int = 7):
    """Get currency trends over specified period"""
    try:
        currency_service = get_currency_service()
        
        trends = currency_service.get_currency_trends(
            currency.upper(),
            days
        )
        
        return trends
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get currency trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to get currency trends")

@router.get("/popular/{region}")
async def get_popular_currencies(region: str):
    """Get popular currencies for a region"""
    try:
        currency_service = get_currency_service()
        
        currencies = currency_service.get_popular_currencies_by_region(region)
        
        # Get full currency info
        supported = currency_service.get_supported_currencies()
        popular_currencies = []
        
        for code in currencies:
            if code in supported:
                popular_currencies.append({
                    'code': code,
                    'symbol': supported[code]['symbol'],
                    'name': supported[code]['name']
                })
        
        return {
            'region': region.upper(),
            'currencies': popular_currencies
        }
    
    except Exception as e:
        logger.error(f"Failed to get popular currencies: {e}")
        raise HTTPException(status_code=500, detail="Failed to get popular currencies")

@router.post("/batch-convert")
async def batch_convert_currencies(amounts: List[Dict[str, Any]]):
    """Convert multiple amounts at once"""
    try:
        currency_service = get_currency_service()
        
        summary = currency_service.get_conversion_summary(amounts)
        
        return summary
    
    except Exception as e:
        logger.error(f"Batch conversion failed: {e}")
        raise HTTPException(status_code=500, detail="Batch conversion failed")

@router.get("/format/{amount}/{currency}")
async def format_currency(amount: float, currency: str):
    """Format amount with proper currency symbol and decimal places"""
    try:
        currency_service = get_currency_service()
        
        formatted = currency_service.format_currency(amount, currency.upper())
        
        return {
            'amount': amount,
            'currency': currency.upper(),
            'formatted': formatted
        }
    
    except Exception as e:
        logger.error(f"Currency formatting failed: {e}")
        raise HTTPException(status_code=500, detail="Currency formatting failed")

@router.post("/update-rates")
async def update_exchange_rates():
    """Manually update exchange rates (admin function)"""
    try:
        currency_service = get_currency_service()
        
        success = currency_service.update_exchange_rates()
        
        return {
            'success': success,
            'last_update': currency_service.last_update.isoformat() if currency_service.last_update else None,
            'message': 'Exchange rates updated successfully' if success else 'Failed to update rates'
        }
    
    except Exception as e:
        logger.error(f"Failed to update exchange rates: {e}")
        raise HTTPException(status_code=500, detail="Failed to update exchange rates")