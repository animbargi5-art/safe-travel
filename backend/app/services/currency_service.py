"""
Currency Service - Real-time currency conversion and multi-currency support
Handles international pricing, currency conversion, and regional pricing
"""

import requests
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from decimal import Decimal, ROUND_HALF_UP
import logging
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

class CurrencyService:
    """
    Real-time currency conversion service with caching and fallback rates
    """
    
    def __init__(self):
        # Supported currencies with their symbols and names
        self.supported_currencies = {
            'USD': {'symbol': '$', 'name': 'US Dollar', 'decimal_places': 2},
            'EUR': {'symbol': '€', 'name': 'Euro', 'decimal_places': 2},
            'GBP': {'symbol': '£', 'name': 'British Pound', 'decimal_places': 2},
            'INR': {'symbol': '₹', 'name': 'Indian Rupee', 'decimal_places': 2},
            'JPY': {'symbol': '¥', 'name': 'Japanese Yen', 'decimal_places': 0},
            'CNY': {'symbol': '¥', 'name': 'Chinese Yuan', 'decimal_places': 2},
            'AUD': {'symbol': 'A$', 'name': 'Australian Dollar', 'decimal_places': 2},
            'CAD': {'symbol': 'C$', 'name': 'Canadian Dollar', 'decimal_places': 2},
            'CHF': {'symbol': 'Fr', 'name': 'Swiss Franc', 'decimal_places': 2},
            'SGD': {'symbol': 'S$', 'name': 'Singapore Dollar', 'decimal_places': 2},
            'AED': {'symbol': 'د.إ', 'name': 'UAE Dirham', 'decimal_places': 2},
            'SAR': {'symbol': 'ر.س', 'name': 'Saudi Riyal', 'decimal_places': 2},
            'THB': {'symbol': '฿', 'name': 'Thai Baht', 'decimal_places': 2},
            'MYR': {'symbol': 'RM', 'name': 'Malaysian Ringgit', 'decimal_places': 2},
            'KRW': {'symbol': '₩', 'name': 'South Korean Won', 'decimal_places': 0},
            'BRL': {'symbol': 'R$', 'name': 'Brazilian Real', 'decimal_places': 2},
            'MXN': {'symbol': '$', 'name': 'Mexican Peso', 'decimal_places': 2},
            'ZAR': {'symbol': 'R', 'name': 'South African Rand', 'decimal_places': 2},
            'RUB': {'symbol': '₽', 'name': 'Russian Ruble', 'decimal_places': 2},
            'TRY': {'symbol': '₺', 'name': 'Turkish Lira', 'decimal_places': 2}
        }
        
        # Exchange rates cache (base currency: USD)
        self.exchange_rates = {}
        self.last_update = None
        self.cache_duration = timedelta(minutes=15)  # Update every 15 minutes
        
        # Fallback rates (in case API fails)
        self.fallback_rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'INR': 83.12,
            'JPY': 110.0,
            'CNY': 7.2,
            'AUD': 1.35,
            'CAD': 1.25,
            'CHF': 0.92,
            'SGD': 1.35,
            'AED': 3.67,
            'SAR': 3.75,
            'THB': 33.5,
            'MYR': 4.2,
            'KRW': 1200.0,
            'BRL': 5.0,
            'MXN': 18.0,
            'ZAR': 15.0,
            'RUB': 75.0,
            'TRY': 8.5
        }
        
        # Regional pricing adjustments
        self.regional_multipliers = {
            'US': 1.0,
            'EU': 1.1,
            'UK': 1.15,
            'IN': 0.3,
            'JP': 1.2,
            'CN': 0.4,
            'AU': 1.25,
            'CA': 1.1,
            'CH': 1.3,
            'SG': 0.9,
            'AE': 0.8,
            'SA': 0.7,
            'TH': 0.25,
            'MY': 0.3,
            'KR': 0.8,
            'BR': 0.4,
            'MX': 0.3,
            'ZA': 0.2,
            'RU': 0.3,
            'TR': 0.2
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Initialize with fallback rates
        self.exchange_rates = self.fallback_rates.copy()
        
        logger.info("💱 Currency Service initialized with 20 supported currencies")
    
    def get_supported_currencies(self) -> Dict[str, Dict[str, Any]]:
        """Get list of supported currencies"""
        return self.supported_currencies
    
    def update_exchange_rates(self) -> bool:
        """Update exchange rates from external API"""
        try:
            # Using a free currency API (you can replace with your preferred provider)
            # For demo purposes, we'll simulate API response
            
            # Simulate API call with realistic rates
            simulated_rates = {
                'USD': 1.0,
                'EUR': 0.85 + (time.time() % 100) * 0.001,  # Slight fluctuation
                'GBP': 0.73 + (time.time() % 50) * 0.001,
                'INR': 83.12 + (time.time() % 200) * 0.01,
                'JPY': 110.0 + (time.time() % 300) * 0.1,
                'CNY': 7.2 + (time.time() % 100) * 0.01,
                'AUD': 1.35 + (time.time() % 80) * 0.001,
                'CAD': 1.25 + (time.time() % 70) * 0.001,
                'CHF': 0.92 + (time.time() % 60) * 0.001,
                'SGD': 1.35 + (time.time() % 90) * 0.001,
                'AED': 3.67 + (time.time() % 40) * 0.01,
                'SAR': 3.75 + (time.time() % 45) * 0.01,
                'THB': 33.5 + (time.time() % 150) * 0.1,
                'MYR': 4.2 + (time.time() % 80) * 0.01,
                'KRW': 1200.0 + (time.time() % 500) * 1.0,
                'BRL': 5.0 + (time.time() % 100) * 0.01,
                'MXN': 18.0 + (time.time() % 200) * 0.01,
                'ZAR': 15.0 + (time.time() % 300) * 0.01,
                'RUB': 75.0 + (time.time() % 1000) * 0.1,
                'TRY': 8.5 + (time.time() % 200) * 0.01
            }
            
            with self._lock:
                self.exchange_rates = simulated_rates
                self.last_update = datetime.utcnow()
            
            logger.info("💱 Exchange rates updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update exchange rates: {e}")
            return False
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return 1.0
        
        # Check if rates need updating
        if (self.last_update is None or 
            datetime.utcnow() - self.last_update > self.cache_duration):
            self.update_exchange_rates()
        
        with self._lock:
            try:
                # Convert via USD (base currency)
                from_rate = self.exchange_rates.get(from_currency, 1.0)
                to_rate = self.exchange_rates.get(to_currency, 1.0)
                
                if from_currency == 'USD':
                    return to_rate
                elif to_currency == 'USD':
                    return 1.0 / from_rate
                else:
                    return to_rate / from_rate
                    
            except (KeyError, ZeroDivisionError):
                logger.warning(f"Exchange rate not found: {from_currency} -> {to_currency}")
                return 1.0
    
    def convert_amount(self, amount: float, from_currency: str, to_currency: str) -> Dict[str, Any]:
        """Convert amount between currencies with detailed information"""
        if from_currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency: {from_currency}")
        
        if to_currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency: {to_currency}")
        
        exchange_rate = self.get_exchange_rate(from_currency, to_currency)
        converted_amount = amount * exchange_rate
        
        # Round to appropriate decimal places
        decimal_places = self.supported_currencies[to_currency]['decimal_places']
        converted_amount = float(Decimal(str(converted_amount)).quantize(
            Decimal('0.01') if decimal_places == 2 else Decimal('1'),
            rounding=ROUND_HALF_UP
        ))
        
        return {
            'original_amount': amount,
            'original_currency': from_currency,
            'converted_amount': converted_amount,
            'target_currency': to_currency,
            'exchange_rate': exchange_rate,
            'currency_symbol': self.supported_currencies[to_currency]['symbol'],
            'formatted_amount': self.format_currency(converted_amount, to_currency),
            'conversion_timestamp': datetime.utcnow().isoformat()
        }
    
    def format_currency(self, amount: float, currency: str) -> str:
        """Format amount with currency symbol and proper decimal places"""
        if currency not in self.supported_currencies:
            return f"{amount:.2f} {currency}"
        
        currency_info = self.supported_currencies[currency]
        symbol = currency_info['symbol']
        decimal_places = currency_info['decimal_places']
        
        if decimal_places == 0:
            formatted = f"{symbol}{int(amount):,}"
        else:
            formatted = f"{symbol}{amount:,.{decimal_places}f}"
        
        return formatted
    
    def get_regional_price(self, base_price_usd: float, region: str, target_currency: str) -> Dict[str, Any]:
        """Get regionally adjusted price in target currency"""
        # Apply regional multiplier
        regional_multiplier = self.regional_multipliers.get(region, 1.0)
        adjusted_price_usd = base_price_usd * regional_multiplier
        
        # Convert to target currency
        conversion_result = self.convert_amount(adjusted_price_usd, 'USD', target_currency)
        
        return {
            **conversion_result,
            'base_price_usd': base_price_usd,
            'regional_multiplier': regional_multiplier,
            'region': region,
            'adjusted_price_usd': adjusted_price_usd
        }
    
    def get_currency_trends(self, currency: str, days: int = 7) -> Dict[str, Any]:
        """Get simulated currency trends (in production, use historical data)"""
        if currency not in self.supported_currencies:
            raise ValueError(f"Unsupported currency: {currency}")
        
        # Simulate trend data
        current_rate = self.get_exchange_rate('USD', currency)
        
        # Generate simulated historical data
        trends = []
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days-i)
            # Simulate rate fluctuation
            fluctuation = (i * 0.01) - (days * 0.005)
            simulated_rate = current_rate * (1 + fluctuation)
            
            trends.append({
                'date': date.isoformat(),
                'rate': round(simulated_rate, 4),
                'change_percent': fluctuation * 100
            })
        
        # Calculate overall trend
        start_rate = trends[0]['rate']
        end_rate = trends[-1]['rate']
        overall_change = ((end_rate - start_rate) / start_rate) * 100
        
        return {
            'currency': currency,
            'current_rate': current_rate,
            'trends': trends,
            'overall_change_percent': round(overall_change, 2),
            'trend_direction': 'up' if overall_change > 0 else 'down' if overall_change < 0 else 'stable'
        }
    
    def get_popular_currencies_by_region(self, region: str) -> List[str]:
        """Get popular currencies for a specific region"""
        regional_currencies = {
            'US': ['USD', 'CAD', 'MXN'],
            'EU': ['EUR', 'GBP', 'CHF'],
            'ASIA': ['INR', 'JPY', 'CNY', 'SGD', 'THB', 'MYR', 'KRW'],
            'MIDDLE_EAST': ['AED', 'SAR'],
            'OCEANIA': ['AUD'],
            'AFRICA': ['ZAR'],
            'SOUTH_AMERICA': ['BRL'],
            'GLOBAL': ['USD', 'EUR', 'GBP', 'INR', 'JPY']
        }
        
        return regional_currencies.get(region.upper(), regional_currencies['GLOBAL'])
    
    def get_conversion_summary(self, amounts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get conversion summary for multiple amounts"""
        conversions = []
        total_usd = 0
        
        for item in amounts:
            amount = item['amount']
            from_currency = item['from_currency']
            to_currency = item.get('to_currency', 'USD')
            
            conversion = self.convert_amount(amount, from_currency, to_currency)
            conversions.append(conversion)
            
            # Convert to USD for total calculation
            if from_currency != 'USD':
                usd_conversion = self.convert_amount(amount, from_currency, 'USD')
                total_usd += usd_conversion['converted_amount']
            else:
                total_usd += amount
        
        return {
            'conversions': conversions,
            'total_usd': total_usd,
            'total_formatted': self.format_currency(total_usd, 'USD'),
            'conversion_count': len(conversions),
            'timestamp': datetime.utcnow().isoformat()
        }

# Global currency service instance
_currency_service = None

def get_currency_service() -> CurrencyService:
    """Get or create currency service instance"""
    global _currency_service
    if _currency_service is None:
        _currency_service = CurrencyService()
    return _currency_service