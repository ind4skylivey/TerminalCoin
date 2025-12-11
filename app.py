import requests
from textual.app import App, ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Header, Footer, Static, DataTable, Label
from textual.reactive import reactive
from textual.message import Message

from news_client import NewsClient # Import the new NewsClient

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
        except Exception as e:
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
        except Exception as e:
            return None

def generate_sparkline(data, width=40):
    if not data:
        return ""
    
    # Resample simple (toma cada N elementos para ajustar al ancho)
    step = max(1, len(data) // width)
    sampled = data[::step][:width]
    
    if not sampled:
        return ""

    min_val = min(sampled)
    max_val = max(sampled)
    diff = max_val - min_val
    
    # Caracteres ASCII de nivel (bloques de altura)
    levels = "  ▂▃▄▅▆▇█"
    
    if diff == 0:
        return levels[4] * len(sampled) # Línea plana
        
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
        
        # Stats formatting
        high_24h = data.get('market_data', {}).get('high_24h', {}).get('usd', 0)
        low_24h = data.get('market_data', {}).get('low_24h', {}).get('usd', 0)
        market_cap = data.get('market_data', {}).get('market_cap', {}).get('usd', 0)
        
        # Sparkline logic
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
        news_list_container.clear()
        
        for item in news_items:
            sentiment_emoji = ""
            if item['sentiment'] == "Bullish":
                sentiment_emoji = "🟢 "
            elif item['sentiment'] == "Bearish":
                sentiment_emoji = "🔴 "
            else:
                sentiment_emoji = "⚪ "
            
            asset_tags = "".join([f"[#00ffff][{asset}][/]" for asset in item['assets']])
            
            news_list_container.mount(
                Label(f"{sentiment_emoji}{asset_tags} [link={item['link']}]{item['title']}[/link] ([#00ff00]{item['source']}[/#00ff00])",
                      classes="news-item")
            )

class TerminalCoinApp(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 1; /* Two columns, one row for the overall screen */
        grid-columns: 1fr 2fr;
        background: #0e1019;
    }
    
    #app-grid { /* Container for the right side, splitting it vertically */
        display: grid;
        grid-rows: 2fr 1fr; /* Top for CoinDetail, Bottom for NewsPanel */
        background: #0e1019;
    }

    /* --- Sidebar (Coin List) --- */
    CoinList {
        height: 100%;
        border: solid #00ff00;
        background: #0e1019;
        margin-right: 1;
    }
    
    .list-header {
        text-align: center;
        background: #00ff00;
        color: #000000;
        text-style: bold;
        padding: 1;
        width: 100%;
        border-bottom: solid #00ff00;
    }

    DataTable {
        height: 100%;
        background: #0e1019;
        scrollbar-gutter: stable;
    }
    
    DataTable > .datatable--header {
        text-style: bold;
        color: #00ffff;
        background: #0e1019;
        border-bottom: solid #00ff00;
    }

    DataTable > .datatable--cursor {
        background: #00ff00;
        color: #000000;
        text-style: bold;
    }

    /* --- Main Content (Detail) --- */
    CoinDetail {
        height: 100%;
        border: solid #00ffff;
        background: #0e1019;
        padding: 2;
        align: center middle;
    }

    #detail-container {
        height: auto;
        border: heavy #00ffff;
        background: #0a0c10;
        padding: 2;
    }

    #coin-name {
        text-align: center;
        text-style: bold;
        color: #00ffff;
        margin-bottom: 1;
        text-opacity: 100%;
        border-bottom: solid #00ffff;
    }

    #coin-price {
        text-align: center;
        text-style: bold;
        color: #00ff00;
        margin-top: 1;
        margin-bottom: 2;
        padding: 1;
        border: dashed #00ff00;
        background: #0e1019;
    }
    
    #coin-stats {
        text-align: left;
        color: #d0d0d0;
        padding: 1;
    }

    #sparkline-label {
        color: #00ff00;
        text-align: center;
        margin-bottom: 1;
        text-opacity: 90%;
    }

    /* --- News Panel --- */
    NewsPanel {
        height: 100%;
        border: solid #9945FF; /* Purple border */
        background: #0e1019;
        margin-top: 1;
    }

    .news-header {
        text-align: center;
        background: #9945FF;
        color: white;
        text-style: bold;
        padding: 1;
        width: 100%;
        border-bottom: solid #9945FF;
    }

    #news-list {
        height: 100%;
        overflow: auto; /* Enable scrolling for news */
        padding: 1;
    }

    .news-item {
        margin-bottom: 1;
        text-overflow: ellipsis; /* Truncate long news titles */
    }
    """

    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh", "Refresh")]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield CoinList()
        with Container(id="app-grid"): # Use a container to hold CoinDetail and NewsPanel vertically
            yield CoinDetail()
            yield NewsPanel()
        yield Footer()

    def on_mount(self) -> None:
        self.load_data()
        self.set_interval(60, self.load_data) # Refresh all data every 60 seconds

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
            # Note: Textual DataTable doesn't support rich tags directly in cells in simple mode easily without Rich objects, 
            # keeping it simple text for now.
            table.add_row(
                str(coin['market_cap_rank']),
                coin['symbol'].upper(),
                price,
                change,
                key=coin['id'] # Store coin ID as row key
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
