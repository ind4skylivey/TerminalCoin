"""
News client for fetching and analyzing cryptocurrency news.

Fetches RSS feeds, performs sentiment analysis, and detects mentioned assets.
"""

from typing import List, Optional, Dict
import feedparser
import httpx
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from config import news_config, CRYPTO_KEYWORDS, SENTIMENT_THRESHOLDS
from models import NewsItem, SentimentType
from exceptions import NetworkException, ParsingException
from logger import get_logger
from utils import sanitize_text, truncate_list

logger = get_logger(__name__)


class SentimentAnalyzer:
    """Handles sentiment analysis for text content."""

    def __init__(self):
        """Initialize sentiment analyzer."""
        try:
            self.analyzer = SentimentIntensityAnalyzer()
            logger.info("Sentiment analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {e}")
            raise

    def analyze(self, text: str) -> SentimentType:
        """
        Analyze sentiment of text.

        Args:
            text: Text to analyze

        Returns:
            SentimentType (Bullish, Bearish, or Neutral)
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided for sentiment analysis")
            return SentimentType.NEUTRAL

        try:
            # Get polarity scores
            scores = self.analyzer.polarity_scores(text)
            compound_score = scores.get('compound', 0.0)

            # Classify sentiment
            if compound_score >= SENTIMENT_THRESHOLDS['bullish']:
                return SentimentType.BULLISH
            elif compound_score <= SENTIMENT_THRESHOLDS['bearish']:
                return SentimentType.BEARISH
            else:
                return SentimentType.NEUTRAL

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return SentimentType.NEUTRAL


class AssetDetector:
    """Detects cryptocurrency assets mentioned in text."""

    def __init__(self, keywords: Optional[Dict[str, str]] = None):
        """
        Initialize asset detector.

        Args:
            keywords: Optional custom keyword mapping
        """
        self.keywords = keywords or CRYPTO_KEYWORDS
        logger.info(f"Asset detector initialized with {len(self.keywords)} keywords")

    def detect(self, text: str) -> List[str]:
        """
        Detect crypto assets mentioned in text.

        Args:
            text: Text to analyze

        Returns:
            List of detected asset symbols (e.g., ['BTC', 'ETH'])
        """
        if not text or not isinstance(text, str):
            return []

        detected = set()
        lower_text = text.lower()

        for keyword, asset_symbol in self.keywords.items():
            # Use word boundaries to avoid partial matches
            if keyword in lower_text:
                detected.add(asset_symbol)

        return sorted(list(detected))


class NewsClient:
    """
    Client for fetching and processing cryptocurrency news from RSS feeds.

    Implements robust error handling, sentiment analysis, and asset detection.
    """

    def __init__(self):
        """Initialize news client with sentiment analyzer and asset detector."""
        self.rss_feeds = news_config.RSS_FEEDS
        self.timeout = news_config.REQUEST_TIMEOUT
        self.max_retries = news_config.MAX_RETRIES

        self.sentiment_analyzer = SentimentAnalyzer()
        self.asset_detector = AssetDetector()

        logger.info(f"News client initialized with {len(self.rss_feeds)} RSS feeds")

    def _fetch_feed(self, source: str, url: str) -> List[Dict]:
        """
        Fetch and parse a single RSS feed.

        Args:
            source: News source name
            url: RSS feed URL

        Returns:
            List of parsed feed entries
        """
        try:
            logger.debug(f"Fetching feed from {source}: {url}")

            # Use httpx for async-ready HTTP requests
            response = httpx.get(
                url,
                timeout=self.timeout,
                follow_redirects=True
            )
            response.raise_for_status()

            # Parse feed
            feed = feedparser.parse(response.text)

            if not feed.entries:
                logger.warning(f"No entries found in feed from {source}")
                return []

            logger.info(f"Successfully fetched {len(feed.entries)} entries from {source}")
            return feed.entries

        except httpx.TimeoutException as e:
            logger.error(f"Timeout fetching feed from {source}: {e}")
            raise NetworkException(
                f"Timeout fetching news from {source}",
                details={"source": source, "error": str(e)}
            )

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error fetching feed from {source}: {e}")
            raise NetworkException(
                f"Failed to fetch news from {source}",
                details={"source": source, "status_code": e.response.status_code}
            )

        except Exception as e:
            logger.error(f"Unexpected error fetching feed from {source}: {e}")
            return []

    def _process_entry(self, entry, source: str) -> Optional[NewsItem]:
        """
        Process a single feed entry into a NewsItem.

        Args:
            entry: Feed entry object
            source: News source name

        Returns:
            NewsItem object or None if processing fails
        """
        try:
            # Extract basic fields with safe defaults
            title = sanitize_text(getattr(entry, 'title', 'No Title'))
            link = getattr(entry, 'link', '#')
            summary = sanitize_text(
                getattr(entry, 'summary', getattr(entry, 'description', ''))
            )

            # Combine title and summary for analysis
            full_text = f"{title} {summary}"

            # Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze(full_text)

            # Detect mentioned assets
            assets = self.asset_detector.detect(full_text)

            # Create NewsItem
            news_item = NewsItem(
                source=source,
                title=title,
                link=link,
                summary=summary,
                sentiment=sentiment,
                assets=assets
            )

            return news_item

        except Exception as e:
            logger.error(f"Error processing news entry: {e}")
            return None

    def fetch_news(self, limit: int = 10) -> List[NewsItem]:
        """
        Fetch news from all configured RSS feeds.

        Args:
            limit: Maximum number of news items per feed

        Returns:
            List of NewsItem objects
        """
        if limit < 1:
            logger.warning(f"Invalid limit {limit}, using default")
            limit = news_config.DEFAULT_NEWS_LIMIT

        all_news: List[NewsItem] = []

        for source, url in self.rss_feeds.items():
            try:
                entries = self._fetch_feed(source, url)

                # Process entries
                for entry in entries[:limit]:
                    news_item = self._process_entry(entry, source)
                    if news_item:
                        all_news.append(news_item)

            except NetworkException as e:
                logger.warning(f"Skipping {source} due to network error: {e.message}")
                continue

            except Exception as e:
                logger.error(f"Unexpected error processing {source}: {e}")
                continue

        logger.info(f"Fetched total of {len(all_news)} news items")

        # Sort by sentiment (Bullish first, then Bearish, then Neutral)
        sentiment_order = {
            SentimentType.BULLISH: 0,
            SentimentType.BEARISH: 1,
            SentimentType.NEUTRAL: 2
        }
        all_news.sort(key=lambda x: sentiment_order.get(x.sentiment, 3))

        return all_news


# Singleton instance for easy import
_news_client_instance: Optional[NewsClient] = None


def get_news_client() -> NewsClient:
    """
    Get or create singleton NewsClient instance.

    Returns:
        NewsClient instance
    """
    global _news_client_instance
    if _news_client_instance is None:
        _news_client_instance = NewsClient()
    return _news_client_instance
