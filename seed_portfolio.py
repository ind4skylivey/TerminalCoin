"""
Seed Portfolio Script.

Populates the TerminalCoin database with example transactions
to demonstrate the portfolio tracking features.
"""

import logging
from database import Database
from portfolio_manager import PortfolioManager

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def seed_data():
    logger.info("Seeding portfolio with example data...")

    # Initialize DB and Manager
    db = Database()
    manager = PortfolioManager(db)

    # Clear existing data (optional, for clean slate)
    # db._get_connection().execute("DELETE FROM holdings")
    # db._get_connection().execute("DELETE FROM transactions")

    # Example Transactions
    # 1. Bitcoin: Bought early and accumulated
    manager.add_transaction("bitcoin", "BTC", "BUY", 0.1, 45000.00)  # $4,500
    manager.add_transaction("bitcoin", "BTC", "BUY", 0.05, 62000.00) # $3,100

    # 2. Ethereum: Bought and sold some
    manager.add_transaction("ethereum", "ETH", "BUY", 5.0, 2800.00)  # $14,000
    manager.add_transaction("ethereum", "ETH", "SELL", 1.0, 3500.00) # Profit taking

    # 3. Solana: High growth play
    manager.add_transaction("solana", "SOL", "BUY", 50.0, 85.00)     # $4,250

    # 4. Cardano: Bag holding (example of loss)
    manager.add_transaction("cardano", "ADA", "BUY", 1000.0, 1.20)   # $1,200 (likely down now)

    # 5. Dogecoin: Meme trade
    manager.add_transaction("dogecoin", "DOGE", "BUY", 5000.0, 0.15) # $750

    logger.info("Portfolio seeded successfully!")
    logger.info("Run 'python app.py' and check the Portfolio tab.")

if __name__ == "__main__":
    seed_data()
