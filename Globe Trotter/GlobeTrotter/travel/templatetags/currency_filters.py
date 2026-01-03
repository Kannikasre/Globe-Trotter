from django import template
from travel.currency_utils import convert_currency, format_currency, get_currency_symbol

register = template.Library()


@register.filter
def convert(amount, currencies):
    """
    Convert currency amount
    Usage: {{ amount|convert:"USD,EUR" }}
    """
    if not currencies or ',' not in currencies:
        return amount
    
    from_currency, to_currency = currencies.split(',')
    try:
        return convert_currency(amount, from_currency.strip(), to_currency.strip())
    except:
        return amount


@register.filter
def currency_format(amount, currency_code='USD'):
    """
    Format amount with currency symbol
    Usage: {{ amount|currency_format:"USD" }}
    """
    try:
        return format_currency(float(amount), currency_code)
    except:
        return f"${amount}"


@register.filter
def currency_symbol(currency_code):
    """
    Get currency symbol
    Usage: {{ "USD"|currency_symbol }}
    """
    return get_currency_symbol(currency_code)
