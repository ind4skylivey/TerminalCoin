import requests
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.reactive import reactive
from textual.message import Message
from textual.theme import Theme
from rich.markup import escape

from news_client import NewsClient

# =============================================================================
# CUSTOM THEMES - Using Textual's Native Theme System
# =============================================================================
# These themes appear in the command palette (Ctrl+P -> search "theme")
# Colors are optimized for readability with good contrast

CUSTOM_THEMES = {
    "matrix": Theme(
        name="matrix",
        primary="#00ff00",          # Bright green (classic hacker)
        secondary="#00cc88",        # Softer green for secondary
        accent="#00ffff",           # Cyan accent
        warning="#ffcc00",          # Yellow warning
        error="#ff4444",            # Red error
        success="#00ff00",          # Green success
        foreground="#e8e8e8",       # Light gray for readability
        background="#0a0f0a",       # Very dark green-tinted black
        surface="#0f1a0f",          # Slightly lighter surface
        panel="#152015",            # Panel background
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
        primary="#ff00aa",          # Hot pink
        secondary="#00ddff",        # Electric cyan
        accent="#ffee00",           # Neon yellow
        warning="#ff9900",          # Orange
        error="#ff3366",            # Pink-red
        success="#00ff88",          # Neon green
        foreground="#f0f0f0",       # Bright white for contrast
        background="#0a0015",       # Deep purple-black
        surface="#150025",          # Purple tinted
        panel="#200035",            # Lighter purple
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
        primary="#00aaff",          # Ocean blue
        secondary="#00ddaa",        # Sea green
        accent="#ff8855",           # Coral/sunset
        warning="#ffbb33",          # Sandy yellow
        error="#ff5566",            # Coral red
        success="#00dd88",          # Sea foam
        foreground="#e0eef8",       # Light blue-white
        background="#050a12",       # Deep ocean black
        surface="#0a1520",          # Dark blue
        panel="#102030",            # Ocean depth
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
        primary="#ffaa00",          # Golden sun
        secondary="#ff7700",        # Warm orange
        accent="#ffdd00",           # Bright yellow
        warning="#ff9900",          # Orange
        error="#ff4433",            # Fire red
        success="#aadd00",          # Lime
        foreground="#fff5e0",       # Warm white
        background="#0f0a05",       # Warm black
        surface="#1a1008",          # Dark brown
        panel="#251810",            # Ember
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
        primary="#aa77ff",          # Soft purple
        secondary="#ff77aa",        # Soft pink
        accent="#77ddff",           # Sky blue
        warning="#ffaa55",          # Peach
        error="#ff6677",            # Soft red
        success="#77dd99",          # Soft green
        foreground="#eee8f5",       # Lavender white
        background="#0a0510",       # Deep purple-black
        surface="#120818",          # Dark purple
        panel="#1a1020",            # Lighter purple
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
        primary="#ffffff",          # Pure white
        secondary="#bbbbbb",        # Light gray
        accent="#888888",           # Medium gray
        warning="#cccccc",          # Light gray
        error="#999999",            # Gray
        success="#dddddd",          # Almost white
        foreground="#e0e0e0",       # Light gray text
        background="#080808",       # Near black
        surface="#121212",          # Dark gray
        panel="#1a1a1a",            # Slightly lighter
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


class CoinGeckoClient:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def get_top_coins(self, limit=50):
        try:
            url = f"{self.BASE_URL}/coins/markets"
            params = {
                "vs_currency": "usd",
                "order": "market_cap_desc",
                "per_page": limit,
                "page": 1,
                "sparkline": "false"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return []

    def get_coin_details(self, coin_id):
        try:
            url = f"{self.BASE_URL}/coins/{coin_id}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "true"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


def generate_sparkline(data, width=40):
    if not data:
        return ""

    step = max(1, len(data) // width)
    sampled = data[::step][:width]

    if not sampled:
        return ""

    min_val = min(sampled)
    max_val = max(sampled)
    diff = max_val - min_val

    levels = "  ▂▃▄▅▆▇█"

    if diff == 0:
        return levels[4] * len(sampled)

    sparkline = ""
    for val in sampled:
        normalized = (val - min_val) / diff
        index = int(normalized * (len(levels) - 1))
        sparkline += levels[index]

    return sparkline


class CoinList(Static):
    def compose(self) -> ComposeResult:
        yield Label("Market Cap Top 50", classes="list-header")
        yield DataTable()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Rank", "Symbol", "Price", "24h %")


class CoinDetail(Static):
    coin_data = reactive(None)

    def compose(self) -> ComposeResult:
        yield Container(
            Label("Select a coin to view details", id="coin-name"),
            Label("", id="coin-price"),
            Label("", id="sparkline-label"),
            Label("", id="coin-stats"),
            id="detail-container"
        )

    def watch_coin_data(self, data: dict) -> None:
        if not data:
            return

        name = f"{data.get('name')} ({data.get('symbol').upper()})"
        price = f"${data.get('market_data', {}).get('current_price', {}).get('usd', 0):,.2f}"

        high_24h = data.get('market_data', {}).get('high_24h', {}).get('usd', 0)
        low_24h = data.get('market_data', {}).get('low_24h', {}).get('usd', 0)
        market_cap = data.get('market_data', {}).get('market_cap', {}).get('usd', 0)

        prices_7d = data.get('market_data', {}).get('sparkline_7d', {}).get('price', [])
        sparkline_art = generate_sparkline(prices_7d, width=50)

        stats_text = (
            f"High 24h: ${high_24h:,.2f}\n"
            f"Low 24h:  ${low_24h:,.2f}\n"
            f"Mkt Cap:  ${market_cap:,.0f}"
        )

        self.query_one("#coin-name", Label).update(name)
        self.query_one("#coin-price", Label).update(price)
        self.query_one("#sparkline-label", Label).update(f"[7 Day Trend]\n{sparkline_art}")
        self.query_one("#coin-stats", Label).update(stats_text)


class NewsPanel(Static):
    news_data = reactive([])

    def compose(self) -> ComposeResult:
        yield Label("Latest Crypto News", classes="news-header")
        yield Container(id="news-list")

    def watch_news_data(self, news_items: list) -> None:
        news_list_container = self.query_one("#news-list", Container)
        news_list_container.remove_children()

        for item in news_items:
            sentiment_emoji = ""
            if item['sentiment'] == "Bullish":
                sentiment_emoji = "🟢 "
            elif item['sentiment'] == "Bearish":
                sentiment_emoji = "🔴 "
            else:
                sentiment_emoji = "⚪ "

            # Escape content to prevent Rich markup errors
            safe_assets = [escape(asset) for asset in item['assets']]
            asset_tags = " ".join([f"[$accent][{asset}][/]" for asset in safe_assets])
            safe_title = escape(item['title'])
            safe_source = escape(item['source'])

            # Simple styled display
            news_list_container.mount(
                Label(f"{sentiment_emoji}{asset_tags} [bold]{safe_title}[/] [dim]({safe_source})[/]",
                      classes="news-item", markup=True)
            )


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
        super().__init__()
        # Register all custom themes
        for theme in CUSTOM_THEMES.values():
            self.register_theme(theme)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield CoinList()
        with Container(id="app-grid"):
            yield CoinDetail()
            yield NewsPanel()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted."""
        # Set default theme to matrix
        self.theme = "matrix"
        self.load_data()
        self.set_interval(60, self.load_data)
        self.notify("Press Ctrl+P and type 'theme' to change colors", timeout=3)

    def load_data(self) -> None:
        self.load_coins()
        self.load_news()

    def load_coins(self) -> None:
        client = CoinGeckoClient()
        coins = client.get_top_coins()

        table = self.query_one(DataTable)
        table.clear()

        for coin in coins:
            price = f"${coin['current_price']:,.2f}"
            change = f"{coin['price_change_percentage_24h']:.2f}%"
            table.add_row(
                str(coin['market_cap_rank']),
                coin['symbol'].upper(),
                price,
                change,
                key=coin['id']
            )

    def load_news(self) -> None:
        client = NewsClient()
        news_items = client.fetch_news(limit=5)
        self.query_one(NewsPanel).news_data = news_items

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        coin_id = event.row_key.value
        if coin_id:
            self.fetch_and_show_details(coin_id)

    def fetch_and_show_details(self, coin_id):
        client = CoinGeckoClient()
        data = client.get_coin_details(coin_id)
        if data:
            self.query_one(CoinDetail).coin_data = data


if __name__ == "__main__":
    app = TerminalCoinApp()
    app.run()
