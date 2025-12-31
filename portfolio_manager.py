"""
Portfolio Manager for TerminalCoin.

Handles business logic for portfolio tracking, P&L calculations,
and interaction with the database.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from database import Database
from api_client import CoinGeckoClient
from logger import get_logger

logger = get_logger(__name__)


@dataclass
class PortfolioItem:
    """Represents a single holding with performance metrics."""
    coin_id: str
    symbol: str
    amount: float
    avg_buy_price: float
    current_price: float = 0.0
    current_value: float = 0.0
    pnl: float = 0.0
    pnl_percent: float = 0.0


class PortfolioManager:
    """Manages portfolio operations and calculations."""

    def __init__(self, db: Database = None):
        """Initialize portfolio manager."""
        self.db = db or Database()
        logger.info("Portfolio Manager initialized")

    def add_transaction(self, coin_id: str, symbol: str, type: str, amount: float, price: float) -> bool:
        """
        Add a new transaction (Buy/Sell).

        Args:
            coin_id: Coin identifier (e.g., 'bitcoin')
            symbol: Coin symbol (e.g., 'BTC')
            type: 'BUY' or 'SELL'
            amount: Amount of coins
            price: Price per coin in USD

        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.add_transaction(
                coin_id=coin_id,
                symbol=symbol.upper(),
                type=type.upper(),
                amount=amount,
                price=price
            )
            return True
        except Exception as e:
            logger.error(f"Failed to add transaction: {e}")
            return False

    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> List[PortfolioItem]:
        """
        Get portfolio holdings with calculated P&L based on current prices.

        Args:
            current_prices: Dictionary mapping coin_id to current price

        Returns:
            List of PortfolioItem objects
        """
        holdings = self.db.get_holdings()
        summary = []

        for holding in holdings:
            coin_id = holding['coin_id']
            amount = holding['amount']
            avg_price = holding['average_buy_price']

            # Get current price (default to buy price if not available to avoid scary numbers)
            current_price = current_prices.get(coin_id, avg_price)

            # Calculate metrics
            current_value = amount * current_price
            cost_basis = amount * avg_price
            pnl = current_value - cost_basis

            pnl_percent = 0.0
            if cost_basis > 0:
                pnl_percent = (pnl / cost_basis) * 100

            item = PortfolioItem(
                coin_id=coin_id,
                symbol=holding['symbol'],
                amount=amount,
                avg_buy_price=avg_price,
                current_price=current_price,
                current_value=current_value,
                pnl=pnl,
                pnl_percent=pnl_percent
            )
            summary.append(item)

        return summary

    def get_total_balance(self, items: List[PortfolioItem]) -> float:
        """Calculate total portfolio balance."""
        return sum(item.current_value for item in items)

    def get_total_pnl(self, items: List[PortfolioItem]) -> float:
        """Calculate total portfolio P&L."""
        return sum(item.pnl for item in items)
