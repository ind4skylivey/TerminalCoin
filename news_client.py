import feedparser
import httpx # A modern HTTP client

class NewsClient:
    RSS_FEEDS = {
        "CoinDesk": "https://www.coindesk.com/feed",
        "CoinTelegraph": "https://cointelegraph.com/rss",
        # "Decrypt": "https://decrypt.co/feed" # Another option if more sources are needed
    }

    def fetch_news(self, limit=10):
        all_news = []
        for source, url in self.RSS_FEEDS.items():
            try:
                # Use httpx to fetch the RSS feed content
                response = httpx.get(url, timeout=10)
                response.raise_for_status() # Raise an exception for HTTP errors
                
                # Parse the feed content directly from the response text
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:limit]: # Take top 'limit' entries per source
                    title = getattr(entry, 'title', 'No Title')
                    link = getattr(entry, 'link', '#')
                    # Some feeds use 'summary', others 'description'
                    summary = getattr(entry, 'summary', getattr(entry, 'description', 'No summary available.'))
                    
                    all_news.append({
                        "source": source,
                        "title": title,
                        "link": link,
                        "summary": summary
                    })
            except Exception as e:
                # print(f"Error fetching news from {source}: {e}") # For debugging
                pass # Fail silently for the user in the app

        # Sort news by publication date if available, or just return as is
        # feedparser entries often have 'published_parsed' or 'updated_parsed'
        # For simplicity, returning unsorted by source for now.
        return all_news[:limit * len(self.RSS_FEEDS)] # Limit total news items

if __name__ == "__main__":
    client = NewsClient()
    news_items = client.fetch_news(limit=5)
    for news in news_items:
        print(f"[{news['source']}] {news['title']} - {news['link']}")
