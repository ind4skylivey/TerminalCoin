"""
Test script for Analysis Engine (v3.0 Phase 1).

Fetches real data from CoinGecko and calculates technical indicators.
"""

import sys
import logging
from api_client import CoinGeckoClient
from analysis_engine import AnalysisEngine

# Configure logging to console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_analysis():
    coin_id = "bitcoin"
    days = 100  # Need enough data for SMA-50

    logger.info(f"Fetching {days} days of history for {coin_id}...")

    api = CoinGeckoClient()
    engine = AnalysisEngine()

    try:
        # 1. Fetch Data
        data = api.get_historical_data(coin_id, days=days)
        prices_data = data.get("prices", [])

        if not prices_data:
            logger.error("No price data returned")
            return

        # Extract just prices and dates
        # CoinGecko returns [timestamp, price]
        dates = [p[0] for p in prices_data]
        prices = [p[1] for p in prices_data]

        logger.info(f"Got {len(prices)} data points. Latest price: ${prices[-1]:,.2f}")

        # 2. Calculate Indicators
        logger.info("Calculating technical indicators...")
        indicators = engine.calculate_indicators(prices)

        # 3. Display Results
        print("\n" + "="*40)
        print(f"TECHNICAL ANALYSIS: {coin_id.upper()}")
        print("="*40)

        print(f"RSI (14):      {indicators.rsi:.2f}")
        print(f"MACD:          {indicators.macd:.2f}")
        print(f"MACD Signal:   {indicators.macd_signal:.2f}")
        print(f"MACD Hist:     {indicators.macd_hist:.2f}")
        print(f"EMA (20):      ${indicators.ema_20:,.2f}")
        print(f"SMA (50):      ${indicators.sma_50:,.2f}")

        # Bollinger Bands
        print(f"BB Upper:      ${indicators.bb_upper:,.2f}")
        print(f"BB Lower:      ${indicators.bb_lower:,.2f}")

        # Signal
        signal = engine.get_signal(indicators)
        print(f"\nSIGNAL:        {signal}")
        print("="*40 + "\n")

    except Exception as e:
        logger.error(f"Test failed: {e}")
    finally:
        api.close()

if __name__ == "__main__":
    test_analysis()
