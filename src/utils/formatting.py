from typing import Union, Any

def format_number(number=0, decimals=2):
    """Format a number with commas and specified decimals"""
    data = float(number)

    if data is None:
        return "N/A"
    
    # Handle large numbers more elegantly
    if data >= 1_000_000_000_000:  # Trillions
        return f"{data / 1_000_000_000_000:.2f}T"
    elif data >= 1_000_000_000:  # Billions
        return f"{data / 1_000_000_000:.2f}B"
    elif data >= 1_000_000:  # Millions
        return f"{data / 1_000_000:.2f}M"
    elif data >= 1_000:  # Thousands
        return f"{data / 1_000:.2f}K"
    else:
        return f"{data:,.{decimals}f}"

def format_currency(amount, currency="$", decimals=2):
    """Format an amount as currency"""
    if amount is None:
        return "N/A"
    
    # Handle large numbers more elegantly
    if amount >= 1_000_000_000_000:  # Trillions
        return f"{amount / 1_000_000_000_000:.2f}T"
    elif amount >= 1_000_000_000:  # Billions
        return f"{currency}{amount / 1_000_000_000:.2f}B"
    elif amount >= 1_000_000:  # Millions
        return f"{currency}{amount / 1_000_000:.2f}M"
    elif amount >= 1_000:  # Thousands
        return f"{currency}{amount / 1_000:.2f}K"
    else:
        return f"{currency}{float(amount):,.{decimals}f}"

def format_percentage(value: Union[int, float, Any], decimal_places: int = 2) -> str:
    """Format a value as a percentage with proper formatting"""
    if isinstance(value, (int, float)):
        # Check if value is already a percentage (0-100) or a decimal (0-1)
        if value > 0 and value < 1:
            value *= 100
        return f"{value:.{decimal_places}f}%"
    return str(value)
