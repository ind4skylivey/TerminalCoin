"""
TerminalCoin - A terminal-based cryptocurrency tracker.

A beautiful, secure, and robust TUI application for tracking cryptocurrency
prices and news with multiple theme support.

Author: il1v3y
Version: 2.0.0
"""

import asyncio
from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, DataTable, Label, Button, Input, TabbedContent, TabPane
from textual.reactive import reactive
from textual.theme import Theme
from rich.markup import escape
from datetime import datetime

from api_client import CoinGeckoClient
from news_client import get_news_client
from models import CoinMarketData, CoinDetailData, NewsItem, SentimentType
from config import app_config
from logger import get_logger
from utils import generate_sparkline, format_currency, format_percentage
from exceptions import TerminalCoinException
from widgets.chart import CryptoChart
from widgets.portfolio import PortfolioTable
from portfolio_manager import PortfolioManager

logger = get_logger(__name__)


# =============================================================================
# CUSTOM THEMES - Using Textual's Native Theme System
# =============================================================================

CUSTOM_THEMES = {
    "matrix": Theme(
        name="matrix",
        primary="#00ff00",
        secondary="#00cc88",
        accent="#00ffff",
        warning="#ffcc00",
        error="#ff4444",
        success="#00ff00",
        foreground="#e8e8e8",
        background="#0a0f0a",
        surface="#0f1a0f",
        panel="#152015",
        dark=True,
        variables={
            "block-cursor-background": "#00ff00",
            "block-cursor-foreground": "#000000",
            "footer-key-foreground": "#00ff00",
            "button-color-foreground": "#0a0f0a",
            "border": "#00aa00",
        },
    ),
    "cyberpunk": Theme(
        name="cyberpunk",
        primary="#00ff41",       # Matrix Green
        secondary="#0099ff",     # Neon Blue
        accent="#ff006e",        # Neon Pink
        warning="#ffcc00",
        error="#ff006e",
        success="#00ff41",
        foreground="#e0e0e0",
        background="#050a15",    # Darker BG
        surface="#0a0e27",       # Dark Blue Surface
        panel="#0a0e27",
        dark=True,
        variables={
            "block-cursor-background": "#00ff41",
            "block-cursor-foreground": "#050a15",
            "footer-key-foreground": "#0099ff",
            "button-color-foreground": "#050a15",
            "border": "#1a2f5f",  # Dark Blue Border
        },
    ),
    "ocean-deep": Theme(
        name="ocean-deep",
        primary="#00aaff",
        secondary="#00ddaa",
        accent="#ff8855",
        warning="#ffbb33",
        error="#ff5566",
        success="#00dd88",
        foreground="#e0eef8",
        background="#050a12",
        surface="#0a1520",
        panel="#102030",
        dark=True,
        variables={
            "block-cursor-background": "#00ddaa",
            "block-cursor-foreground": "#050a12",
            "footer-key-foreground": "#00aaff",
            "button-color-foreground": "#050a12",
            "border": "#0088cc",
        },
    ),
    "solar-flare": Theme(
        name="solar-flare",
        primary="#ffaa00",
        secondary="#ff7700",
        accent="#ffdd00",
        warning="#ff9900",
        error="#ff4433",
        success="#aadd00",
        foreground="#fff5e0",
        background="#0f0a05",
        surface="#1a1008",
        panel="#251810",
        dark=True,
        variables={
            "block-cursor-background": "#ff7700",
            "block-cursor-foreground": "#0f0a05",
            "footer-key-foreground": "#ffaa00",
            "button-color-foreground": "#0f0a05",
            "border": "#cc8800",
        },
    ),
    "midnight-purple": Theme(
        name="midnight-purple",
        primary="#aa77ff",
        secondary="#ff77aa",
        accent="#77ddff",
        warning="#ffaa55",
        error="#ff6677",
        success="#77dd99",
        foreground="#eee8f5",
        background="#0a0510",
        surface="#120818",
        panel="#1a1020",
        dark=True,
        variables={
            "block-cursor-background": "#ff77aa",
            "block-cursor-foreground": "#0a0510",
            "footer-key-foreground": "#aa77ff",
            "button-color-foreground": "#0a0510",
            "border": "#8855cc",
        },
    ),
    "monochrome": Theme(
        name="monochrome",
        primary="#ffffff",
        secondary="#bbbbbb",
        accent="#888888",
        warning="#cccccc",
        error="#999999",
        success="#dddddd",
        foreground="#e0e0e0",
        background="#080808",
        surface="#121212",
        panel="#1a1a1a",
        dark=True,
        variables={
            "block-cursor-background": "#ffffff",
            "block-cursor-foreground": "#080808",
            "footer-key-foreground": "#ffffff",
            "button-color-foreground": "#080808",
            "border": "#666666",
        },
    ),
}


# =============================================================================
# UI COMPONENTS
# =============================================================================

class CoinList(Static):
    """Widget displaying list of top cryptocurrencies with search and filters."""

    coins: reactive[list[CoinMarketData]] = reactive([])
    filtered_coins: reactive[list[CoinMarketData]] = reactive([])
    current_sort: reactive[str] = reactive("market_cap")  # market_cap, gainers, losers

    def compose(self) -> ComposeResult:
        """Compose the coin list widget."""
        yield Container(
            Input(placeholder="Search coins...", id="coin-search"),
            Horizontal(
                Button("Mkt Cap", id="sort-cap", variant="primary", classes="sort-btn"),
                Button("Gainers", id="sort-gainers", variant="default", classes="sort-btn"),
                Button("Losers", id="sort-losers", variant="default", classes="sort-btn"),
                classes="filter-bar"
            ),
            id="list-controls"
        )
        yield Label("Market Cap Top 50", classes="list-header", id="list-title")
        yield DataTable()

    def on_mount(self) -> None:
        """Configure the data table on mount."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Rank", "Symbol", "Price", "24h %", "Trend (7d)")
        logger.debug("CoinList widget mounted")

    def watch_coins(self, coins: list[CoinMarketData]) -> None:
        """Update filtered list when raw coins data changes."""
        self._apply_filters()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        self._apply_filters()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle sort button presses."""
        if event.button.id == "sort-cap":
            self.current_sort = "market_cap"
            self.query_one("#list-title", Label).update("Market Cap Top 50")
        elif event.button.id == "sort-gainers":
            self.current_sort = "gainers"
            self.query_one("#list-title", Label).update("Top Gainers (24h)")
        elif event.button.id == "sort-losers":
            self.current_sort = "losers"
            self.query_one("#list-title", Label).update("Top Losers (24h)")

        # Update button styles
        for btn_id in ["sort-cap", "sort-gainers", "sort-losers"]:
            btn = self.query_one(f"#{btn_id}", Button)
            btn.variant = "primary" if btn_id == event.button.id else "default"

        self._apply_filters()

    def _apply_filters(self) -> None:
        """Filter and sort coins based on input and selected category."""
        search_term = self.query_one("#coin-search", Input).value.lower()

        # 1. Filter by search term
        result = [
            c for c in self.coins
            if search_term in c.name.lower() or search_term in c.symbol.lower()
        ]

        # 2. Sort
        if self.current_sort == "gainers":
            result.sort(key=lambda x: x.price_change_percentage_24h or -9999, reverse=True)
        elif self.current_sort == "losers":
            result.sort(key=lambda x: x.price_change_percentage_24h or 9999, reverse=False)
        else: # market_cap (default)
            result.sort(key=lambda x: x.market_cap_rank or 9999, reverse=False)

        self.filtered_coins = result
        self._update_table(result)

    def _update_table(self, coins: list[CoinMarketData]) -> None:
        """Update the DataTable with processed coins."""
        table = self.query_one(DataTable)
        table.clear()

        for coin in coins:
            try:
                price = format_currency(coin.current_price)
                change = format_percentage(coin.price_change_percentage_24h or 0.0)

                # Generate Sparkline
                sparkline = ""
                if coin.sparkline_7d:
                    sparkline = generate_sparkline(coin.sparkline_7d, width=15)

                table.add_row(
                    str(coin.market_cap_rank or "N/A"),
                    coin.symbol,
                    price,
                    change,
                    sparkline,
                    key=coin.id
                )
            except Exception as e:
                logger.warning(f"Error adding coin row: {e}")
                continue
        logger.info(f"Displayed {len(coins)} coins in CoinList")

    async def fetch_coins(self, client: CoinGeckoClient) -> None:
        """Fetch top cryptocurrencies and update the widget asynchronously."""
        try:
            # Fetch more coins to allow for better filtering/sorting locally
            # Use asyncio.to_thread to run the blocking API call in a separate thread
            self.coins = await asyncio.to_thread(client.get_top_coins, limit=100)
            logger.info(f"Fetched {len(self.coins)} coins for CoinList")
        except TerminalCoinException as e:
            logger.error(f"Error loading coins: {e.message}")
            self.app.notify(f"Error loading coins: {e.message}", severity="warning")
        except Exception as e:
            logger.error(f"Unexpected error loading coins: {e}")
            self.app.notify("Error loading coins", severity="error")


class CoinDetail(Static):
    """Widget displaying detailed information for a selected coin."""

    coin_data: reactive[Optional[CoinDetailData]] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the coin detail widget."""
        yield Container(
            Label("Select a coin to view details", id="coin-name"),
            Label("", id="coin-price"),
            # Chart replaces the sparkline label
            CryptoChart(id="price-chart"),
            Label("", id="coin-stats"),
            id="detail-container"
        )

    def watch_coin_data(self, data: Optional[CoinDetailData]) -> None:
        """
        Update display when coin data changes.

        Args:
            data: CoinDetailData object or None
        """
        if not data:
            return

        try:
            # Format coin name and symbol
            name = f"{data.name} ({data.symbol.upper()})"

            # Format price
            price = format_currency(data.current_price)

            # Get 24h high/low and market cap
            high_24h = data.high_24h
            low_24h = data.low_24h
            market_cap = data.market_cap

            # Format stats
            stats_text = (
                f"High 24h: {format_currency(high_24h)}\n"
                f"Low 24h:  {format_currency(low_24h)}\n"
                f"Mkt Cap:  {format_currency(market_cap, decimals=0)}"
            )

            # Update labels
            self.query_one("#coin-name", Label).update(name)
            self.query_one("#coin-price", Label).update(price)
            self.query_one("#coin-stats", Label).update(stats_text)

            logger.debug(f"Updated coin detail for {data.name}")

        except Exception as e:
            logger.error(f"Error updating coin detail: {e}")
            self.notify("Error displaying coin details", severity="error")

    def update_chart(self, prices: list, dates: list):
        """Update the chart with new data."""
        try:
            chart = self.query_one("#price-chart", CryptoChart)
            chart.update_data(prices, dates, title="30 Day History")
        except Exception as e:
            logger.error(f"Error updating chart: {e}")


class NewsPanel(Static):
    """Widget displaying cryptocurrency news feed."""

    news_data: reactive[list] = reactive([])

    def compose(self) -> ComposeResult:
        """Compose the news panel widget."""
        yield Label("Latest Crypto News", classes="news-header")
        yield VerticalScroll(id="news-list")

    def watch_news_data(self, news_items: list) -> None:
        """
        Update display when news data changes.

        Args:
            news_items: List of NewsItem objects
        """
        news_list_container = self.query_one("#news-list", VerticalScroll)
        news_list_container.remove_children()

        for item in news_items:
            try:
                # Sentiment emoji
                sentiment_emoji = {
                    SentimentType.BULLISH: "🟢 ",
                    SentimentType.BEARISH: "🔴 ",
                    SentimentType.NEUTRAL: "⚪ "
                }.get(item.sentiment, "⚪ ")

                # Escape content to prevent Rich markup errors
                safe_assets = [escape(asset) for asset in item.assets]
                asset_tags = " ".join([f"[$accent][{asset}][/]" for asset in safe_assets])
                safe_title = escape(item.title)
                safe_source = escape(item.source)

                # Create news item label
                news_list_container.mount(
                    Label(
                        f"{sentiment_emoji}{asset_tags} [bold]{safe_title}[/] [dim]({safe_source})[/]",
                        classes="news-item",
                        markup=True
                    )
                )
            except Exception as e:
                logger.error(f"Error displaying news item: {e}")
                continue

        logger.debug(f"Updated news panel with {len(news_items)} items")

    async def fetch_news(self, client) -> None:
        """Fetch cryptocurrency news and update the widget asynchronously."""
        try:
            self.news_data = await asyncio.to_thread(client.fetch_news, limit=5)
            logger.info(f"Fetched {len(self.news_data)} news items")
        except Exception as e:
            logger.error(f"Error loading news: {e}")
            # Don't notify user for news errors, fail silently


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class TerminalCoinApp(App):
    """TerminalCoin - A terminal-based cryptocurrency tracker."""

    CSS = """
    /* --- Global Layout --- */
    Screen {
        layout: vertical;
        height: 100%;
        background: $surface;
    }

    /* --- Tab Layout --- */
    TabbedContent {
        height: 1fr;
    }

    TabPane {
        height: 1fr;
        padding: 0;
    }

    /* --- Main Container (Horizontal Split) --- */
    #main-container {
        height: 1fr;
        width: 100%;
        layout: horizontal;
    }

    /* --- Left Pane (Coin List) --- */
    CoinList {
        width: 35%;
        height: 1fr;
        border-right: heavy $primary;
        background: $surface-darken-1;
    }

    #list-controls {
        height: auto;
        padding: 1;
        background: $surface-darken-1;
        border-bottom: solid $primary;
    }

    #coin-search {
        width: 100%;
        margin-bottom: 1;
        background: $surface;
        border: solid $secondary;
        color: $text;
    }

    .filter-bar {
        height: auto;
        width: 100%;
        align: center middle;
    }

    .sort-btn {
        width: 1fr;
        margin: 0 1;
        min-width: 8;
    }

    .list-header {
        text-align: center;
        background: $primary;
        color: $background; /* High contrast text */
        text-style: bold;
        padding: 1;
        width: 100%;
    }

    DataTable {
        height: 1fr;
        width: 100%;
        scrollbar-gutter: stable;
        background: $surface-darken-1;
    }

    DataTable > .datatable--header {
        color: $secondary;
        text-style: bold;
    }

    /* --- Right Pane (Vertical Split) --- */
    #right-pane {
        width: 65%;
        height: 1fr;
        layout: vertical;
    }

    /* --- Coin Detail Section --- */
    CoinDetail {
        height: 60%;
        width: 100%;
        border: heavy $secondary; /* Neon Blue Border */
        background: $surface;
        padding: 1;
    }

    #detail-container {
        height: 1fr;
        width: 100%;
        layout: vertical;
    }

    #coin-name {
        text-align: center;
        text-style: bold;
        background: $surface-lighten-1;
        color: $secondary;
        width: 100%;
        padding: 1;
        border: solid $secondary;
    }

    #coin-price {
        text-align: center;
        text-style: bold;
        color: $primary;
        width: 100%;
        padding: 1;
        border-bottom: dashed $primary;
        margin-bottom: 1;
        background: $surface-darken-1;
    }

    #price-chart {
        height: 1fr;
        width: 100%;
        border: solid $accent;
        margin: 1 0;
        background: $surface-darken-1;
    }

    #coin-stats {
        text-align: left;
        width: 100%;
        padding: 1;
        background: $surface-darken-1;
        border-top: solid $secondary;
        color: $text;
    }

    /* --- News Panel --- */
    NewsPanel {
        height: 40%;
        width: 100%;
        border-top: heavy $primary;
        background: $surface;
        padding: 1;
    }

    .news-header {
        text-align: center;
        background: $secondary;
        color: $background;
        text-style: bold;
        width: 100%;
        padding: 1;
        margin-bottom: 1;
    }

    .news-scroll {
        height: 1fr;
        width: 100%;
        scrollbar-gutter: stable;
    }

    .news-item {
        margin-bottom: 1;
        padding: 1;
        background: $surface-lighten-1;
        border-left: solid $accent;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
        ("p", "command_palette", "Palette"),
    ]

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        # Register all custom themes
        for theme in CUSTOM_THEMES.values():
            self.register_theme(theme)

        # Initialize API clients
        self.coin_client: Optional[CoinGeckoClient] = None
        self.news_client = get_news_client()
        self.portfolio_manager = PortfolioManager()

        logger.info(f"TerminalCoin v{app_config.VERSION} initialized")

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)

        with TabbedContent(initial="market"):
            with TabPane("Market", id="market"):
                # Use Horizontal for main split
                with Horizontal(id="main-container"):
                    yield CoinList()
                    # Use Vertical for right pane split
                    with Vertical(id="right-pane"):
                        yield CoinDetail()
                        yield NewsPanel()

            with TabPane("Portfolio", id="portfolio"):
                yield PortfolioTable()

        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        try:
            # Set default theme
            self.theme = app_config.DEFAULT_THEME

            # Initialize coin client
            self.coin_client = CoinGeckoClient()

            # Load initial data
            self.refresh_data()

            # Set up auto-refresh
            self.set_interval(app_config.REFRESH_INTERVAL, self.refresh_data)

            # Show welcome notification
            self.notify(
                f"Welcome to {app_config.APP_NAME} v{app_config.VERSION}",
                title="Ready",
                severity="information"
            )

            # Set focus to the coin list so keyboard navigation works immediately
            self.query_one(CoinList).focus()

            logger.info("Application mounted successfully")

        except Exception as e:
            logger.error(f"Error during mount: {e}")
            self.notify(f"Error initializing app: {e}", severity="error")

    def refresh_data(self) -> None:
        """Refresh all data sources."""
        self.notify("Refreshing data...", severity="information")

        # 1. Refresh Market Data
        if self.coin_client:
            self.run_worker(self.query_one(CoinList).fetch_coins(self.coin_client), group="refresh")

        # 2. Refresh News
        self.run_worker(self.query_one(NewsPanel).fetch_news(self.news_client), group="refresh")

        # 3. Refresh Portfolio
        self._refresh_portfolio()

    def _refresh_portfolio(self) -> None:
        """Update portfolio view with current prices."""
        try:
            # Create a map of current prices from the coin list
            # Note: Ideally we should fetch specific prices for portfolio coins,
            # but for efficiency we'll use the top coins list if available.
            current_prices = {}
            coin_list_widget = self.query_one(CoinList)
            if coin_list_widget.coins:
                for coin in coin_list_widget.coins:
                    current_prices[coin.id] = coin.current_price

            # Update portfolio table
            items = self.portfolio_manager.get_portfolio_summary(current_prices)
            self.query_one(PortfolioTable).items = items

        except Exception as e:
            logger.error(f"Error refreshing portfolio: {e}")
            self.notify("Error refreshing portfolio", severity="error")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Handle row selection in the coin list.

        Args:
            event: Row selection event
        """
        coin_id = event.row_key.value
        logger.info(f"Row selected: {coin_id}")
        if coin_id:
            self.fetch_and_show_details(coin_id)

    # Cache for coin details: {coin_id: (timestamp, data, history)}
    _coin_details_cache: dict = {}
    CACHE_TTL = 300  # 5 minutes

    def fetch_and_show_details(self, coin_id: str) -> None:
        """
        Fetch and display detailed coin information asynchronously.

        Args:
            coin_id: Coin identifier
        """
        if not self.coin_client:
            logger.warning("Coin client not initialized")
            return

        # Check cache first
        now = datetime.utcnow().timestamp()
        if coin_id in self._coin_details_cache:
            timestamp, data, history = self._coin_details_cache[coin_id]
            if now - timestamp < self.CACHE_TTL:
                logger.info(f"Using cached details for {coin_id}")
                self._update_detail_ui(data, history)
                return

        # Run API calls in a worker thread to avoid freezing UI
        self.run_worker(self._fetch_details_worker(coin_id), exclusive=True, group="coin_fetch")

    def _update_detail_ui(self, data: CoinDetailData, history: dict) -> None:
        """Update the detail UI with provided data."""
        self.query_one(CoinDetail).coin_data = data

        prices_data = history.get("prices", [])
        if prices_data:
            dates = [datetime.fromtimestamp(p[0]/1000).strftime("%d/%m/%Y") for p in prices_data]
            prices = [p[1] for p in prices_data]
            self.query_one(CoinDetail).update_chart(prices, dates)

    async def _fetch_details_worker(self, coin_id: str) -> None:
        """Worker function to fetch details in background."""
        try:
            # 1. Get Basic Details
            data = await asyncio.to_thread(self.coin_client.get_coin_details, coin_id)

            if data:
                # 2. Get Historical Data for Chart (30 days)
                history = await asyncio.to_thread(self.coin_client.get_historical_data, coin_id, days=30)

                # Update Cache
                self._coin_details_cache[coin_id] = (datetime.utcnow().timestamp(), data, history)

                # Update UI
                self._update_detail_ui(data, history)
            else:
                self.notify(f"Could not load details for {coin_id}", severity="warning")

        except TerminalCoinException as e:
            logger.error(f"Error fetching coin details: {e.message}")
            self.notify(f"Error: {e.message}", severity="error")
        except Exception as e:
            logger.error(f"Unexpected error fetching coin details: {e}")
            self.notify("Error loading coin details", severity="error")

    def action_refresh(self) -> None:
        """Refresh all data."""
        self.refresh_data()

    def on_unmount(self) -> None:
        """Clean up when app is unmounted."""
        if self.coin_client:
            self.coin_client.close()
        logger.info("Application unmounted")


def main() -> None:
    """Main entry point for the application."""
    try:
        app = TerminalCoinApp()
        app.run()
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
