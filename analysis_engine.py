"""
Analysis Engine for TerminalCoin.

Handles technical analysis calculations using Pandas and Pandas TA.
Responsible for processing raw price data into actionable indicators.
"""

from typing import Dict, Any, Optional, List
import pandas as pd
import pandas_ta as ta
from dataclasses import dataclass

from logger import get_logger
from exceptions import ParsingException

logger = get_logger(__name__)


@dataclass
class TechnicalIndicators:
    """Container for calculated technical indicators."""
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_hist: Optional[float] = None
    ema_20: Optional[float] = None
    sma_50: Optional[float] = None
    bb_upper: Optional[float] = None
    bb_lower: Optional[float] = None


class AnalysisEngine:
    """
    Core engine for technical analysis.

    Uses pandas-ta to calculate indicators from OHLCV data.
    """

    def __init__(self):
        """Initialize the analysis engine."""
        logger.info("Analysis Engine initialized")

    def prepare_dataframe(self, prices: List[float], dates: List[int] = None) -> pd.DataFrame:
        """
        Convert raw price list to Pandas DataFrame.

        Args:
            prices: List of closing prices
            dates: Optional list of timestamps

        Returns:
            DataFrame with 'close' column
        """
        try:
            if not prices:
                return pd.DataFrame()

            data = {"close": prices}
            if dates and len(dates) == len(prices):
                data["date"] = pd.to_datetime(dates, unit='ms')

            df = pd.DataFrame(data)
            if "date" in df.columns:
                df.set_index("date", inplace=True)

            return df
        except Exception as e:
            logger.error(f"Error preparing dataframe: {e}")
            raise ParsingException("Failed to prepare data for analysis", details={"error": str(e)})

    def calculate_indicators(self, prices: List[float]) -> TechnicalIndicators:
        """
        Calculate technical indicators for a given price series.

        Args:
            prices: List of historical prices (ordered oldest to newest)

        Returns:
            TechnicalIndicators object with latest values
        """
        if not prices or len(prices) < 50:
            logger.warning("Insufficient data for technical analysis (need 50+ points)")
            return TechnicalIndicators()

        try:
            df = self.prepare_dataframe(prices)

            # Calculate Indicators using pandas_ta

            # 1. RSI (14 periods)
            df.ta.rsi(length=14, append=True)

            # 2. MACD (12, 26, 9)
            df.ta.macd(fast=12, slow=26, signal=9, append=True)

            # 3. EMA (20 periods)
            df.ta.ema(length=20, append=True)

            # 4. SMA (50 periods)
            df.ta.sma(length=50, append=True)

            # 5. Bollinger Bands (20, 2.0)
            df.ta.bbands(length=20, std=2.0, append=True)

            # Get the latest values (last row)
            latest = df.iloc[-1]

            # Extract values safely (column names depend on pandas_ta naming convention)
            indicators = TechnicalIndicators(
                rsi=self._safe_float(latest.get("RSI_14")),
                macd=self._safe_float(latest.get("MACD_12_26_9")),
                macd_signal=self._safe_float(latest.get("MACDs_12_26_9")),
                macd_hist=self._safe_float(latest.get("MACDh_12_26_9")),
                ema_20=self._safe_float(latest.get("EMA_20")),
                sma_50=self._safe_float(latest.get("SMA_50")),
                bb_upper=self._safe_float(latest.get("BBU_20_2.0")),
                bb_lower=self._safe_float(latest.get("BBL_20_2.0"))
            )

            logger.debug(f"Calculated indicators: RSI={indicators.rsi:.2f} MACD={indicators.macd:.2f}")
            return indicators

        except Exception as e:
            logger.error(f"Error calculating indicators: {e}")
            return TechnicalIndicators()

    def _safe_float(self, value: Any) -> Optional[float]:
        """Convert numpy/pandas types to standard float safely."""
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_signal(self, indicators: TechnicalIndicators) -> str:
        """
        Generate a simple trading signal based on indicators.

        Returns:
            "BUY", "SELL", or "NEUTRAL"
        """
        score = 0

        # RSI Logic
        if indicators.rsi:
            if indicators.rsi < 30: score += 1  # Oversold -> Buy
            elif indicators.rsi > 70: score -= 1  # Overbought -> Sell

        # MACD Logic
        if indicators.macd and indicators.macd_signal:
            if indicators.macd > indicators.macd_signal: score += 1 # Bullish crossover
            elif indicators.macd < indicators.macd_signal: score -= 1 # Bearish crossover

        # EMA Trend Logic
        # (Requires current price comparison, implemented in UI logic usually)

        if score >= 1: return "BUY"
        if score <= -1: return "SELL"
        return "NEUTRAL"
