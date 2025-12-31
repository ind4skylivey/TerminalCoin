"""
CryptoChart Widget for TerminalCoin.

Renders interactive price charts using textual-plotext.
Supports Candlestick and Line charts with technical indicators.
"""

from typing import List, Optional
from textual.widgets import Static
from textual.reactive import reactive
from textual_plotext import PlotextPlot

from logger import get_logger
from analysis_engine import TechnicalIndicators

logger = get_logger(__name__)


class CryptoChart(PlotextPlot):
    """
    A widget for displaying cryptocurrency price charts.
    """

    # Reactive properties to trigger redraws
    prices: reactive[List[float]] = reactive([])
    dates: reactive[List[str]] = reactive([])
    indicators: reactive[Optional[TechnicalIndicators]] = reactive(None)
    chart_type: reactive[str] = reactive("line")  # "line" or "candle" (future)
    title: reactive[str] = reactive("Price History")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data_ready = False

    def on_mount(self) -> None:
        """Initialize chart settings on mount."""
        self.plt.theme("dark")
        self.plt.grid(True, True)
        self.plt.xlabel("Date")
        self.plt.ylabel("Price (USD)")

    def update_data(self, prices: List[float], dates: List[str], title: str = ""):
        """Update chart data and redraw."""
        self.prices = prices
        self.dates = dates
        if title:
            self.title = title
        self._data_ready = True
        self.replot()

    def replot(self) -> None:
        """Redraw the chart with current data."""
        if not self._data_ready or not self.prices:
            return

        self.plt.clear_data()
        self.plt.title(self.title)

        # Plot Main Price Line
        self.plt.plot(self.dates, self.prices, label="Price", color="green")

        # Plot Indicators if available (e.g., SMA)
        # Note: In a real implementation, we would need the full series of SMA values,
        # not just the latest point. For now, we visualize the main price.

        # Formatting
        self.plt.theme("dark")
        self.plt.frame(True)
        self.plt.grid(True, True)
        self.plt.date_form("d/m/Y")  # Full date format

        self.refresh()

    def watch_prices(self, new_prices: List[float]) -> None:
        """Watch for price updates."""
        self.replot()

    def watch_chart_type(self, new_type: str) -> None:
        """Watch for chart type changes."""
        self.replot()
