"""
Portfolio Widget for TerminalCoin.

Displays portfolio holdings and performance metrics in a table.
"""

from typing import List
from textual.widgets import Static, DataTable, Label
from textual.containers import Container
from textual.reactive import reactive
from rich.text import Text

from portfolio_manager import PortfolioItem
from utils import format_currency, format_percentage
from logger import get_logger

logger = get_logger(__name__)


class PortfolioTable(Static):
    """Widget displaying portfolio holdings."""

    items: reactive[List[PortfolioItem]] = reactive([])

    def compose(self):
        yield Label("My Portfolio", id="portfolio-title")
        yield DataTable(id="portfolio-table")
        yield Container(
            Label("Total Balance: $0.00", id="total-balance"),
            Label("Total P&L: $0.00 (0.00%)", id="total-pnl"),
            id="portfolio-summary"
        )

    def on_mount(self):
        """Initialize table columns."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns(
            "Symbol",
            "Amount",
            "Avg Price",
            "Current Price",
            "Value",
            "P&L",
            "P&L %"
        )

    def watch_items(self, new_items: List[PortfolioItem]):
        """Update table when items change."""
        table = self.query_one(DataTable)
        table.clear()

        total_value = 0.0
        total_cost = 0.0

        for item in new_items:
            total_value += item.current_value
            total_cost += (item.amount * item.avg_buy_price)

            # Colorize P&L
            pnl_color = "green" if item.pnl >= 0 else "red"
            pnl_text = Text(format_currency(item.pnl), style=pnl_color)
            pnl_pct_text = Text(format_percentage(item.pnl_percent), style=pnl_color)

            table.add_row(
                item.symbol,
                f"{item.amount:.4f}",
                format_currency(item.avg_buy_price),
                format_currency(item.current_price),
                format_currency(item.current_value),
                pnl_text,
                pnl_pct_text
            )

        # Update Summary
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0.0

        pnl_color = "green" if total_pnl >= 0 else "red"

        self.query_one("#total-balance").update(f"Total Balance: {format_currency(total_value)}")
        self.query_one("#total-pnl").update(
            f"Total P&L: [{pnl_color}]{format_currency(total_pnl)} ({format_percentage(total_pnl_pct)})[/{pnl_color}]"
        )
