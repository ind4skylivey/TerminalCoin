"""
Data models for TerminalCoin application.

Uses Pydantic for data validation and type safety.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment classification types."""
    BULLISH = "Bullish"
    BEARISH = "Bearish"
    NEUTRAL = "Neutral"


class CoinMarketData(BaseModel):
    """Model for cryptocurrency market data from CoinGecko."""

    model_config = ConfigDict(extra='ignore')

    id: str = Field(..., description="Coin identifier")
    symbol: str = Field(..., description="Coin symbol (e.g., BTC)")
    name: str = Field(..., description="Coin name (e.g., Bitcoin)")
    current_price: float = Field(..., gt=0, description="Current price in USD")
    market_cap_rank: Optional[int] = Field(None, ge=1, description="Market cap rank")
    market_cap: Optional[float] = Field(None, ge=0, description="Market capitalization")
    price_change_percentage_24h: Optional[float] = Field(None, description="24h price change %")

    @field_validator('symbol')
    @classmethod
    def symbol_uppercase(cls, v: str) -> str:
        """Ensure symbol is uppercase."""
        return v.upper() if v else v


class CoinDetailData(BaseModel):
    """Model for detailed cryptocurrency information."""

    model_config = ConfigDict(extra='ignore')

    id: str = Field(..., description="Coin identifier")
    symbol: str = Field(..., description="Coin symbol")
    name: str = Field(..., description="Coin name")
    market_data: Dict[str, Any] = Field(..., description="Market data dictionary")

    @property
    def current_price(self) -> float:
        """Extract current price from market data."""
        return self.market_data.get('current_price', {}).get('usd', 0.0)

    @property
    def high_24h(self) -> float:
        """Extract 24h high from market data."""
        return self.market_data.get('high_24h', {}).get('usd', 0.0)

    @property
    def low_24h(self) -> float:
        """Extract 24h low from market data."""
        return self.market_data.get('low_24h', {}).get('usd', 0.0)

    @property
    def market_cap(self) -> float:
        """Extract market cap from market data."""
        return self.market_data.get('market_cap', {}).get('usd', 0.0)

    @property
    def sparkline_7d(self) -> List[float]:
        """Extract 7-day sparkline data."""
        return self.market_data.get('sparkline_7d', {}).get('price', [])


class NewsItem(BaseModel):
    """Model for cryptocurrency news item."""

    model_config = ConfigDict(extra='ignore')

    source: str = Field(..., min_length=1, description="News source name")
    title: str = Field(..., min_length=1, description="News title")
    link: str = Field(..., description="News article URL")
    summary: str = Field(default="", description="News summary")
    sentiment: SentimentType = Field(default=SentimentType.NEUTRAL, description="Sentiment analysis")
    assets: List[str] = Field(default_factory=list, description="Related crypto assets")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")

    @field_validator('link')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Basic URL validation."""
        if not v.startswith(('http://', 'https://', '#')):
            raise ValueError(f"Invalid URL format: {v}")
        return v

    @field_validator('assets')
    @classmethod
    def validate_assets(cls, v: List[str]) -> List[str]:
        """Ensure assets are uppercase and unique."""
        return list(set(asset.upper() for asset in v))


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    success: bool = Field(..., description="Request success status")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
