"""
CoinGecko API client with rate limiting and error handling.

Provides a robust interface to the CoinGecko API with retry logic,
rate limiting, and comprehensive error handling.
"""

from typing import List, Optional, Dict, Any
import time
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import api_config
from exceptions import (
    APIException,
    NetworkException,
    RateLimitException,
    DataNotFoundException,
    ValidationException
)
from models import CoinMarketData, CoinDetailData
from logger import get_logger
from utils import validate_coin_id

logger = get_logger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls."""

    def __init__(self, max_calls: int, period: int):
        """
        Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: List[datetime] = []

    def __call__(self, func):
        """Decorator to apply rate limiting."""
        def wrapper(*args, **kwargs):
            self._wait_if_needed()
            return func(*args, **kwargs)
        return wrapper

    def _wait_if_needed(self) -> None:
        """Wait if rate limit would be exceeded."""
        now = datetime.utcnow()

        # Remove old calls outside the time window
        self.calls = [
            call_time for call_time in self.calls
            if now - call_time < timedelta(seconds=self.period)
        ]

        # Check if we need to wait
        if len(self.calls) >= self.max_calls:
            sleep_time = (self.calls[0] + timedelta(seconds=self.period) - now).total_seconds()
            if sleep_time > 0:
                logger.warning(f"Rate limit reached. Waiting {sleep_time:.2f}s")
                time.sleep(sleep_time)
                self.calls = []

        self.calls.append(now)


class CoinGeckoClient:
    """
    Client for interacting with CoinGecko API.

    Implements rate limiting, retry logic, and comprehensive error handling.
    """

    def __init__(self):
        """Initialize CoinGecko client with session and rate limiter."""
        self.base_url = api_config.COINGECKO_BASE_URL
        self.timeout = api_config.REQUEST_TIMEOUT
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(
            max_calls=api_config.RATE_LIMIT_CALLS,
            period=api_config.RATE_LIMIT_PERIOD
        )
        logger.info("CoinGecko client initialized")

    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry strategy.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=api_config.MAX_RETRIES,
            backoff_factor=api_config.RETRY_DELAY,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update({
            'User-Agent': 'TerminalCoin/2.0',
            'Accept': 'application/json'
        })

        return session

    def _make_request(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to CoinGecko API.

        Args:
            endpoint: API endpoint path
            params: Optional query parameters

        Returns:
            JSON response data

        Raises:
            APIException: For API errors
            NetworkException: For network errors
            RateLimitException: For rate limit errors
        """
        url = f"{self.base_url}/{endpoint}"

        try:
            self.rate_limiter._wait_if_needed()

            logger.debug(f"Making request to {url} with params {params}")
            response = self.session.get(
                url,
                params=params,
                timeout=self.timeout
            )

            # Handle rate limiting
            if response.status_code == 429:
                logger.error("Rate limit exceeded")
                raise RateLimitException(
                    "API rate limit exceeded. Please try again later.",
                    details={"status_code": 429}
                )

            # Handle not found
            if response.status_code == 404:
                logger.warning(f"Resource not found: {url}")
                raise DataNotFoundException(
                    "Requested data not found",
                    details={"endpoint": endpoint}
                )

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise NetworkException(
                "Request timed out. Please check your connection.",
                details={"error": str(e)}
            )

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkException(
                "Failed to connect to API. Please check your internet connection.",
                details={"error": str(e)}
            )

        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            raise APIException(
                f"API request failed: {e}",
                details={"status_code": response.status_code}
            )

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise APIException(
                f"Unexpected error occurred: {e}",
                details={"error": str(e)}
            )

    def get_top_coins(self, limit: int = 50) -> List[CoinMarketData]:
        """
        Fetch top cryptocurrencies by market cap.

        Args:
            limit: Number of coins to fetch (max 250)

        Returns:
            List of CoinMarketData objects

        Raises:
            ValidationException: If limit is invalid
            APIException: For API errors
        """
        # Validate limit
        if not isinstance(limit, int) or limit < 1:
            raise ValidationException(
                "Limit must be a positive integer",
                details={"provided_limit": limit}
            )

        if limit > api_config.MAX_COINS_LIMIT:
            logger.warning(f"Limit {limit} exceeds maximum, capping at {api_config.MAX_COINS_LIMIT}")
            limit = api_config.MAX_COINS_LIMIT

        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false"
        }

        try:
            data = self._make_request("coins/markets", params)

            # Validate and parse response
            coins = []
            for coin_data in data:
                try:
                    coin = CoinMarketData(**coin_data)
                    coins.append(coin)
                except Exception as e:
                    logger.warning(f"Failed to parse coin data: {e}")
                    continue

            logger.info(f"Successfully fetched {len(coins)} coins")
            return coins

        except Exception as e:
            logger.error(f"Failed to fetch top coins: {e}")
            return []

    def get_coin_details(self, coin_id: str) -> Optional[CoinDetailData]:
        """
        Fetch detailed information for a specific coin.

        Args:
            coin_id: Coin identifier (e.g., 'bitcoin')

        Returns:
            CoinDetailData object or None if not found

        Raises:
            ValidationException: If coin_id is invalid
        """
        # Validate coin ID
        if not validate_coin_id(coin_id):
            raise ValidationException(
                "Invalid coin ID format",
                details={"coin_id": coin_id}
            )

        params = {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
            "sparkline": "true"
        }

        try:
            data = self._make_request(f"coins/{coin_id}", params)
            coin_detail = CoinDetailData(**data)
            logger.info(f"Successfully fetched details for {coin_id}")
            return coin_detail

        except DataNotFoundException:
            logger.warning(f"Coin not found: {coin_id}")
            return None

        except Exception as e:
            logger.error(f"Failed to fetch coin details for {coin_id}: {e}")
            return None

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()
        logger.info("CoinGecko client session closed")
