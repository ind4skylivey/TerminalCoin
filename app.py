"""
TerminalCoin - A terminal-based cryptocurrency tracker.

A beautiful, secure, and robust TUI application for tracking cryptocurrency
prices and news with multiple theme support.

Author: il1v3y
Version: 2.0.0
"""

from typing import Optional
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.reactive import reactive
from textual.theme import Theme
from rich.markup import escape

from api_client import CoinGeckoClient
from news_client import get_news_client
from models import CoinMarketData, CoinDetailData, NewsItem, SentimentType
from config import app_config
from logger import get_logger
from utils import generate_sparkline, format_currency, format_percentage
from exceptions import TerminalCoinException

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
        primary="#ff00aa",
        secondary="#00ddff",
        accent="#ffee00",
        warning="#ff9900",
        error="#ff3366",
        success="#00ff88",
        foreground="#f0f0f0",
        background="#0a0015",
        surface="#150025",
        panel="#200035",
        dark=True,
        variables={
            "block-cursor-background": "#00ddff",
            "block-cursor-foreground": "#0a0015",
            "footer-key-foreground": "#ff00aa",
            "button-color-foreground": "#0a0015",
            "border": "#aa0077",
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
    """Widget displaying list of top cryptocurrencies."""

    def compose(self) -> ComposeResult:
        """Compose the coin list widget."""
        yield Label("Market Cap Top 50", classes="list-header")
        yield DataTable()

    def on_mount(self) -> None:
        """Configure the data table on mount."""
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Rank", "Symbol", "Price", "24h %")
        logger.debug("CoinList widget mounted")


class CoinDetail(Static):
    """Widget displaying detailed information for a selected coin."""

    coin_data: reactive[Optional[CoinDetailData]] = reactive(None)

    def compose(self) -> ComposeResult:
        """Compose the coin detail widget."""
        yield Container(
            Label("Select a coin to view details", id="coin-name"),
            Label("", id="coin-price"),
            Label("", id="sparkline-label"),
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

            # Generate sparkline
            prices_7d = data.sparkline_7d
            sparkline_art = generate_sparkline(prices_7d, width=50) if prices_7d else "No data"

            # Format stats
            stats_text = (
                f"High 24h: {format_currency(high_24h)}\n"
                f"Low 24h:  {format_currency(low_24h)}\n"
                f"Mkt Cap:  {format_currency(market_cap, decimals=0)}"
            )

            # Update labels
            self.query_one("#coin-name", Label).update(name)
            self.query_one("#coin-price", Label).update(price)
            self.query_one("#sparkline-label", Label).update(f"[7 Day Trend]\n{sparkline_art}")
            self.query_one("#coin-stats", Label).update(stats_text)

            logger.debug(f"Updated coin detail for {data.name}")

        except Exception as e:
            logger.error(f"Error updating coin detail: {e}")
            self.notify("Error displaying coin details", severity="error")


class NewsPanel(Static):
    """Widget displaying cryptocurrency news feed."""

    news_data: reactive[list] = reactive([])

    def compose(self) -> ComposeResult:
        """Compose the news panel widget."""
        yield Label("Latest Crypto News", classes="news-header")
        yield Container(id="news-list")

    def watch_news_data(self, news_items: list) -> None:
        """
        Update display when news data changes.

        Args:
            news_items: List of NewsItem objects
        """
        news_list_container = self.query_one("#news-list", Container)
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


# =============================================================================
# MAIN APPLICATION
# =============================================================================

class TerminalCoinApp(App):
    """TerminalCoin - A terminal-based cryptocurrency tracker."""

    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1;
        grid-columns: 1fr 2fr;
    }

    #app-grid {
        layout: grid;
        grid-rows: 2fr 1fr;
    }

    /* --- Sidebar (Coin List) --- */
    CoinList {
        height: 100%;
        border: solid $primary;
        margin-right: 1;
    }

    .list-header {
        text-align: center;
        background: $primary;
        color: $background;
        text-style: bold;
        padding: 1;
        width: 100%;
    }

    DataTable {
        height: 100%;
        scrollbar-gutter: stable;
    }

    DataTable > .datatable--header {
        text-style: bold;
        color: $secondary;
    }

    DataTable > .datatable--cursor {
        background: $primary;
        color: $background;
        text-style: bold;
    }

    /* --- Main Content (Detail) --- */
    CoinDetail {
        height: 100%;
        border: solid $secondary;
        padding: 2;
        align: center middle;
    }

    #detail-container {
        height: auto;
        border: heavy $secondary;
        background: $surface;
        padding: 2;
    }

    #coin-name {
        text-align: center;
        text-style: bold;
        color: $secondary;
        margin-bottom: 1;
        border-bottom: solid $secondary;
    }

    #coin-price {
        text-align: center;
        text-style: bold;
        color: $primary;
        margin-top: 1;
        margin-bottom: 2;
        padding: 1;
        border: dashed $primary;
    }

    #coin-stats {
        text-align: left;
        padding: 1;
    }

    #sparkline-label {
        color: $success;
        text-align: center;
        margin-bottom: 1;
    }

    /* --- News Panel --- */
    NewsPanel {
        height: 100%;
        border: solid $accent;
        margin-top: 1;
    }

    .news-header {
        text-align: center;
        background: $accent;
        color: $background;
        text-style: bold;
        padding: 1;
        width: 100%;
    }

    #news-list {
        height: 100%;
        overflow: auto;
        padding: 1;
    }

    .news-item {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
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

        logger.info(f"TerminalCoin v{app_config.VERSION} initialized")

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header(show_clock=True)
        yield CoinList()
        with Container(id="app-grid"):
            yield CoinDetail()
            yield NewsPanel()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        try:
            # Set default theme
            self.theme = app_config.DEFAULT_THEME

            # Initialize coin client
            self.coin_client = CoinGeckoClient()

            # Load initial data
            self.load_data()

            # Set up auto-refresh
            self.set_interval(app_config.REFRESH_INTERVAL, self.load_data)

            # Show welcome notification
            self.notify(
                "Press Ctrl+P and type 'theme' to change colors",
                timeout=3
            )

            logger.info("Application mounted successfully")

        except Exception as e:
            logger.error(f"Error during mount: {e}")
            self.notify(f"Error initializing app: {e}", severity="error")

    def load_data(self) -> None:
        """Load coin and news data."""
        try:
            self.load_coins()
            self.load_news()
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            self.notify("Error loading data", severity="error")

    def load_coins(self) -> None:
        """Load top cryptocurrencies."""
        if not self.coin_client:
            logger.warning("Coin client not initialized")
            return

        try:
            coins = self.coin_client.get_top_coins(limit=50)

            table = self.query_one(DataTable)
            table.clear()

            for coin in coins:
                try:
                    price = format_currency(coin.current_price)
                    change = format_percentage(coin.price_change_percentage_24h or 0.0)

                    table.add_row(
                        str(coin.market_cap_rank or "N/A"),
                        coin.symbol,
                        price,
                        change,
                        key=coin.id
                    )
                except Exception as e:
                    logger.warning(f"Error adding coin row: {e}")
                    continue

            logger.info(f"Loaded {len(coins)} coins")

        except TerminalCoinException as e:
            logger.error(f"Error loading coins: {e.message}")
            self.notify(f"Error loading coins: {e.message}", severity="warning")
        except Exception as e:
            logger.error(f"Unexpected error loading coins: {e}")

    def load_news(self) -> None:
        """Load cryptocurrency news."""
        try:
            news_items = self.news_client.fetch_news(limit=5)
            self.query_one(NewsPanel).news_data = news_items
            logger.info(f"Loaded {len(news_items)} news items")

        except Exception as e:
            logger.error(f"Error loading news: {e}")
            # Don't notify user for news errors, fail silently

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        Handle row selection in the coin list.

        Args:
            event: Row selection event
        """
        coin_id = event.row_key.value
        if coin_id:
            self.fetch_and_show_details(coin_id)

    def fetch_and_show_details(self, coin_id: str) -> None:
        """
        Fetch and display detailed coin information.

        Args:
            coin_id: Coin identifier
        """
        if not self.coin_client:
            logger.warning("Coin client not initialized")
            return

        try:
            data = self.coin_client.get_coin_details(coin_id)
            if data:
                self.query_one(CoinDetail).coin_data = data
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
        self.notify("Refreshing data...")
        self.load_data()

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
