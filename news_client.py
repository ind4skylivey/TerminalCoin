import feedparser
import httpx # A modern HTTP client
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class NewsClient:
    RSS_FEEDS = {
        "CoinDesk": "https://www.coindesk.com/feed",
        "CoinTelegraph": "https://cointelegraph.com/rss",
        # "Decrypt": "https://decrypt.co/feed" # Another option if more sources are needed
    }

    # Keywords for asset detection (case-insensitive)
    CRYPTO_KEYWORDS = {
        "bitcoin": "BTC", "btc": "BTC",
        "ethereum": "ETH", "eth": "ETH",
        "solana": "SOL", "sol": "SOL",
        "bnb": "BNB", "binance coin": "BNB",
        "ripple": "XRP", "xrp": "XRP",
        "cardano": "ADA", "ada": "ADA",
        "dogecoin": "DOGE", "doge": "DOGE",
        "shiba inu": "SHIB", "shib": "SHIB"
    }

    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def _analyze_sentiment(self, text):
        vs = self.analyzer.polarity_scores(text)
        compound_score = vs['compound']
        if compound_score >= 0.05:
            return "Bullish" # Positive
        elif compound_score <= -0.05:
            return "Bearish" # Negative
        else:
            return "Neutral" # Neutral

    def _detect_assets(self, text):
        detected = set()
        lower_text = text.lower()
        for keyword, asset_symbol in self.CRYPTO_KEYWORDS.items():
            if keyword in lower_text:
                detected.add(asset_symbol)
        return list(detected)

    def fetch_news(self, limit=10):
        all_news = []
        for source, url in self.RSS_FEEDS.items():
            try:
                response = httpx.get(url, timeout=10)
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:limit]:
                    title = getattr(entry, 'title', 'No Title')
                    link = getattr(entry, 'link', '#')
                    summary = getattr(entry, 'summary', getattr(entry, 'description', 'No summary available.'))
                    
                    sentiment = self._analyze_sentiment(title + " " + summary)
                    assets = self._detect_assets(title + " " + summary)

                    all_news.append({
                        "source": source,
                        "title": title,
                        "link": link,
                        "summary": summary,
                        "sentiment": sentiment,
                        "assets": assets
                    })
            except Exception as e:
                # print(f"Error fetching news from {source}: {e}") # For debugging
                pass # Fail silently for the user in the app

        # Sort news by publication date if available, or just return as is
        # For simplicity, returning unsorted by source for now.
        return all_news[:limit * len(self.RSS_FEEDS)] # Limit total news items

if __name__ == "__main__":
    client = NewsClient()
    news_items = client.fetch_news(limit=5)
    for news in news_items:
        print(f"[{news['source']}] {news['sentiment']} {news['assets']} {news['title']} - {news['link']}")