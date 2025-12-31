"""
Database layer for TerminalCoin.

Handles SQLite connection and schema management for portfolio tracking.
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from logger import get_logger
from config import app_config

logger = get_logger(__name__)

DB_FILE = "terminalcoin.db"

class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = DB_FILE):
        """Initialize database connection."""
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Table: Holdings (Current state)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS holdings (
                        coin_id TEXT PRIMARY KEY,
                        symbol TEXT NOT NULL,
                        amount REAL NOT NULL,
                        average_buy_price REAL NOT NULL,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Table: Transactions (History)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS transactions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        coin_id TEXT NOT NULL,
                        symbol TEXT NOT NULL,
                        type TEXT NOT NULL,  -- 'BUY' or 'SELL'
                        amount REAL NOT NULL,
                        price_per_coin REAL NOT NULL,
                        total_value REAL NOT NULL,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                logger.info("Database schema initialized")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    def add_transaction(self, coin_id: str, symbol: str, type: str, amount: float, price: float) -> None:
        """Record a transaction and update holdings."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # 1. Record Transaction
                total = amount * price
                cursor.execute("""
                    INSERT INTO transactions (coin_id, symbol, type, amount, price_per_coin, total_value, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (coin_id, symbol, type, amount, price, total, datetime.utcnow()))

                # 2. Update Holdings
                # Get current holding
                cursor.execute("SELECT * FROM holdings WHERE coin_id = ?", (coin_id,))
                current = cursor.fetchone()

                if type == 'BUY':
                    if current:
                        # Calculate new weighted average price
                        new_amount = current['amount'] + amount
                        total_cost = (current['amount'] * current['average_buy_price']) + (amount * price)
                        new_avg_price = total_cost / new_amount

                        cursor.execute("""
                            UPDATE holdings
                            SET amount = ?, average_buy_price = ?, updated_at = ?
                            WHERE coin_id = ?
                        """, (new_amount, new_avg_price, datetime.utcnow(), coin_id))
                    else:
                        # New holding
                        cursor.execute("""
                            INSERT INTO holdings (coin_id, symbol, amount, average_buy_price)
                            VALUES (?, ?, ?, ?)
                        """, (coin_id, symbol, amount, price))

                elif type == 'SELL':
                    if current:
                        new_amount = current['amount'] - amount
                        if new_amount <= 0:
                            # Sold everything
                            cursor.execute("DELETE FROM holdings WHERE coin_id = ?", (coin_id,))
                        else:
                            # Update amount (avg price doesn't change on sell)
                            cursor.execute("""
                                UPDATE holdings
                                SET amount = ?, updated_at = ?
                                WHERE coin_id = ?
                            """, (new_amount, datetime.utcnow(), coin_id))

                conn.commit()
                logger.info(f"Transaction recorded: {type} {amount} {symbol} @ ${price}")

        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise

    def get_holdings(self) -> List[Dict[str, Any]]:
        """Get all current holdings."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM holdings ORDER BY amount * average_buy_price DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch holdings: {e}")
            return []

    def get_transactions(self, coin_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get transaction history."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                if coin_id:
                    cursor.execute("SELECT * FROM transactions WHERE coin_id = ? ORDER BY timestamp DESC", (coin_id,))
                else:
                    cursor.execute("SELECT * FROM transactions ORDER BY timestamp DESC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to fetch transactions: {e}")
            return []
