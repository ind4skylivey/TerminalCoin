"""
Utility functions for TerminalCoin application.

Contains helper functions for data processing, validation, and formatting.
"""

from typing import List, Optional
import re
from functools import lru_cache

from config import SPARKLINE_CHARS, SPARKLINE_DEFAULT_WIDTH
from logger import get_logger

logger = get_logger(__name__)


def generate_sparkline(
    data: List[float],
    width: int = SPARKLINE_DEFAULT_WIDTH
) -> str:
    """
    Generate ASCII sparkline from numerical data.

    Args:
        data: List of numerical values
        width: Maximum width of sparkline

    Returns:
        ASCII sparkline string

    Raises:
        ValueError: If data is empty or invalid
    """
    if not data:
        logger.warning("Empty data provided for sparkline generation")
        return ""

    if not all(isinstance(x, (int, float)) for x in data):
        logger.error("Invalid data types in sparkline data")
        raise ValueError("All data points must be numeric")

    # Sample data to fit width
    step = max(1, len(data) // width)
    sampled = data[::step][:width]

    if not sampled:
        return ""

    min_val = min(sampled)
    max_val = max(sampled)
    diff = max_val - min_val

    # Handle flat line case
    if diff == 0:
        middle_char = SPARKLINE_CHARS[len(SPARKLINE_CHARS) // 2]
        return middle_char * len(sampled)

    # Generate sparkline
    sparkline = ""
    for val in sampled:
        normalized = (val - min_val) / diff
        index = int(normalized * (len(SPARKLINE_CHARS) - 1))
        index = max(0, min(index, len(SPARKLINE_CHARS) - 1))  # Clamp to valid range
        sparkline += SPARKLINE_CHARS[index]

    return sparkline


def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize text by removing potentially harmful characters.

    Args:
        text: Input text to sanitize
        max_length: Optional maximum length

    Returns:
        Sanitized text string
    """
    if not isinstance(text, str):
        logger.warning(f"Non-string value provided to sanitize_text: {type(text)}")
        return str(text)

    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)

    # Truncate if needed
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."

    return sanitized.strip()


def format_currency(
    value: float,
    decimals: int = 2,
    symbol: str = "$"
) -> str:
    """
    Format a number as currency.

    Args:
        value: Numerical value
        decimals: Number of decimal places
        symbol: Currency symbol

    Returns:
        Formatted currency string
    """
    try:
        if decimals == 0:
            return f"{symbol}{value:,.0f}"
        return f"{symbol}{value:,.{decimals}f}"
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting currency: {e}")
        return f"{symbol}0.00"


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format a number as percentage.

    Args:
        value: Numerical value
        decimals: Number of decimal places

    Returns:
        Formatted percentage string with sign
    """
    try:
        sign = "+" if value > 0 else ""
        return f"{sign}{value:.{decimals}f}%"
    except (ValueError, TypeError) as e:
        logger.error(f"Error formatting percentage: {e}")
        return "0.00%"


@lru_cache(maxsize=128)
def validate_coin_id(coin_id: str) -> bool:
    """
    Validate coin ID format.

    Args:
        coin_id: Coin identifier to validate

    Returns:
        True if valid, False otherwise
    """
    if not coin_id or not isinstance(coin_id, str):
        return False

    # Coin IDs should be lowercase alphanumeric with hyphens
    pattern = r'^[a-z0-9-]+$'
    return bool(re.match(pattern, coin_id))


def truncate_list(items: List, max_items: int) -> List:
    """
    Safely truncate a list to maximum items.

    Args:
        items: List to truncate
        max_items: Maximum number of items

    Returns:
        Truncated list
    """
    if not isinstance(items, list):
        logger.warning(f"Non-list provided to truncate_list: {type(items)}")
        return []

    if max_items < 0:
        logger.warning(f"Negative max_items provided: {max_items}")
        max_items = 0

    return items[:max_items]


def safe_get(dictionary: dict, *keys, default=None):
    """
    Safely get nested dictionary values.

    Args:
        dictionary: Dictionary to query
        *keys: Sequence of keys to traverse
        default: Default value if key not found

    Returns:
        Value at nested key or default

    Example:
        safe_get(data, 'market_data', 'current_price', 'usd', default=0.0)
    """
    result = dictionary
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key)
            if result is None:
                return default
        else:
            return default
    return result if result is not None else default
