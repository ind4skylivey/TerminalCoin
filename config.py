"""
Configuration module for TerminalCoin application.

This module centralizes all configuration settings, API endpoints,
and application constants following security best practices.
"""

import os
from typing import Final
from dataclasses import dataclass


# API Configuration
@dataclass(frozen=True)
class APIConfig:
    """API configuration with immutable settings."""

    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 1

    # Rate limiting
    RATE_LIMIT_CALLS: int = 50
    RATE_LIMIT_PERIOD: int = 60  # seconds

    # Pagination
    DEFAULT_COINS_LIMIT: int = 50
    MAX_COINS_LIMIT: int = 250
    DEFAULT_NEWS_LIMIT: int = 5
    MAX_NEWS_LIMIT: int = 20


@dataclass(frozen=True)
class NewsConfig:
    """News feed configuration."""

    RSS_FEEDS: dict = None
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 2

    def __post_init__(self):
        """Initialize RSS feeds after dataclass creation."""
        if self.RSS_FEEDS is None:
            # Use object.__setattr__ for frozen dataclass
            object.__setattr__(self, 'RSS_FEEDS', {
                "CoinDesk": "https://www.coindesk.com/feed",
                "CoinTelegraph": "https://cointelegraph.com/rss",
            })


@dataclass(frozen=True)
class AppConfig:
    """Application-wide configuration."""

    APP_NAME: str = "TerminalCoin"
    VERSION: str = "2.0.0"

    # UI Configuration
    REFRESH_INTERVAL: int = 60  # seconds
    DEFAULT_THEME: str = "matrix"

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "terminalcoin.log")

    # Cache settings
    CACHE_TTL: int = 300  # 5 minutes
    ENABLE_CACHE: bool = True


# Sentiment Analysis Configuration
SENTIMENT_THRESHOLDS: Final[dict] = {
    "bullish": 0.05,
    "bearish": -0.05,
}

# Crypto Keywords for Asset Detection
CRYPTO_KEYWORDS: Final[dict] = {
    "bitcoin": "BTC", "btc": "BTC",
    "ethereum": "ETH", "eth": "ETH",
    "solana": "SOL", "sol": "SOL",
    "bnb": "BNB", "binance coin": "BNB",
    "ripple": "XRP", "xrp": "XRP",
    "cardano": "ADA", "ada": "ADA",
    "dogecoin": "DOGE", "doge": "DOGE",
    "shiba inu": "SHIB", "shib": "SHIB",
    "polkadot": "DOT", "dot": "DOT",
    "avalanche": "AVAX", "avax": "AVAX",
}

# Sparkline Configuration
SPARKLINE_CHARS: Final[str] = "  ▂▃▄▅▆▇█"
SPARKLINE_DEFAULT_WIDTH: Final[int] = 40

# Initialize configuration instances
api_config = APIConfig()
news_config = NewsConfig()
app_config = AppConfig()
