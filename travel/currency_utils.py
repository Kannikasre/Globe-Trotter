"""
Currency converter utility for GlobeTrotter
Provides currency conversion functionality using exchange rates
"""

import requests
from decimal import Decimal
from django.core.cache import cache

# Common currencies
CURRENCIES = [
    ('USD', 'US Dollar ($)'),
    ('EUR', 'Euro (€)'),
    ('GBP', 'British Pound (£)'),
    ('JPY', 'Japanese Yen (¥)'),
    ('CNY', 'Chinese Yuan (¥)'),
    ('INR', 'Indian Rupee (₹)'),
    ('CAD', 'Canadian Dollar ($)'),
    ('AUD', 'Australian Dollar ($)'),
    ('CHF', 'Swiss Franc (Fr)'),
    ('MXN', 'Mexican Peso ($)'),
    ('BRL', 'Brazilian Real (R$)'),
    ('ZAR', 'South African Rand (R)'),
    ('SGD', 'Singapore Dollar ($)'),
    ('HKD', 'Hong Kong Dollar ($)'),
    ('NZD', 'New Zealand Dollar ($)'),
    ('SEK', 'Swedish Krona (kr)'),
    ('NOK', 'Norwegian Krone (kr)'),
    ('KRW', 'South Korean Won (₩)'),
    ('TRY', 'Turkish Lira (₺)'),
    ('RUB', 'Russian Ruble (₽)'),
    ('AED', 'UAE Dirham (د.إ)'),
    ('THB', 'Thai Baht (฿)'),
    ('PLN', 'Polish Zloty (zł)'),
    ('DKK', 'Danish Krone (kr)'),
]

# Fallback exchange rates (relative to USD)
FALLBACK_RATES = {
    'USD': 1.0,
    'EUR': 0.92,
    'GBP': 0.79,
    'JPY': 149.50,
    'CNY': 7.24,
    'INR': 83.12,
    'CAD': 1.35,
    'AUD': 1.52,
    'CHF': 0.88,
    'MXN': 17.15,
    'BRL': 4.98,
    'ZAR': 18.75,
    'SGD': 1.34,
    'HKD': 7.82,
    'NZD': 1.64,
    'SEK': 10.45,
    'NOK': 10.68,
    'KRW': 1320.50,
    'TRY': 32.15,
    'RUB': 92.50,
    'AED': 3.67,
    'THB': 35.80,
    'PLN': 4.02,
    'DKK': 6.87,
}


def get_exchange_rates():
    """
    Get current exchange rates from cache or API
    Returns dict with currency codes as keys and rates (relative to USD) as values
    """
    # Try to get from cache first
    rates = cache.get('exchange_rates')
    if rates:
        return rates
    
    # Try to fetch from API (using exchangerate-api.com free tier)
    try:
        response = requests.get(
            'https://api.exchangerate-api.com/v4/latest/USD',
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', FALLBACK_RATES)
            # Cache for 24 hours
            cache.set('exchange_rates', rates, 60 * 60 * 24)
            return rates
    except Exception as e:
        print(f"Error fetching exchange rates: {e}")
    
    # Use fallback rates
    return FALLBACK_RATES


def convert_currency(amount, from_currency, to_currency):
    """
    Convert amount from one currency to another
    
    Args:
        amount: Amount to convert (Decimal or float)
        from_currency: Source currency code (e.g., 'USD')
        to_currency: Target currency code (e.g., 'EUR')
    
    Returns:
        Decimal: Converted amount
    """
    if from_currency == to_currency:
        return Decimal(str(amount))
    
    amount = Decimal(str(amount))
    rates = get_exchange_rates()
    
    # Get rates, default to 1.0 if not found
    from_rate = Decimal(str(rates.get(from_currency, 1.0)))
    to_rate = Decimal(str(rates.get(to_currency, 1.0)))
    
    # Convert: amount -> USD -> target currency
    amount_in_usd = amount / from_rate
    converted_amount = amount_in_usd * to_rate
    
    return converted_amount.quantize(Decimal('0.01'))


def get_currency_symbol(currency_code):
    """Get currency symbol for a currency code"""
    symbols = {
        'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'CNY': '¥',
        'INR': '₹', 'CAD': '$', 'AUD': '$', 'CHF': 'Fr', 'MXN': '$',
        'BRL': 'R$', 'ZAR': 'R', 'SGD': '$', 'HKD': '$', 'NZD': '$',
        'SEK': 'kr', 'NOK': 'kr', 'KRW': '₩', 'TRY': '₺', 'RUB': '₽',
        'AED': 'د.إ', 'THB': '฿', 'PLN': 'zł', 'DKK': 'kr',
    }
    return symbols.get(currency_code, currency_code)


def format_currency(amount, currency_code):
    """Format amount with currency symbol"""
    symbol = get_currency_symbol(currency_code)
    return f"{symbol}{amount:,.2f}"
