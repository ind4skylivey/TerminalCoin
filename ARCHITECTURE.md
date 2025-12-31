# TerminalCoin - Code Architecture

## Project Structure

```
TerminalCoin/
├── __init__.py           # Package initialization
├── app.py                # Main application and UI components
├── api_client.py         # CoinGecko API client with rate limiting
├── news_client.py        # RSS news fetcher with sentiment analysis
├── models.py             # Pydantic data models
├── config.py             # Configuration and constants
├── exceptions.py         # Custom exception hierarchy
├── logger.py             # Logging utilities
├── utils.py              # Helper functions
├── requirements.txt      # Python dependencies
├── SECURITY.md          # Security policy
└── README.md            # Project documentation
```

## Architecture Principles

### 1. **Separation of Concerns**

Each module has a single, well-defined responsibility:

- `app.py`: UI and application logic
- `api_client.py`: External API communication
- `news_client.py`: News fetching and analysis
- `models.py`: Data structures and validation
- `config.py`: Configuration management
- `utils.py`: Reusable helper functions

### 2. **Clean Code Practices**

#### Type Hints

All functions use type hints for better IDE support and type checking:

```python
def format_currency(value: float, decimals: int = 2, symbol: str = "$") -> str:
    ...
```

#### Docstrings

All modules, classes, and functions have comprehensive docstrings:

```python
def generate_sparkline(data: List[float], width: int = 40) -> str:
    """
    Generate ASCII sparkline from numerical data.

    Args:
        data: List of numerical values
        width: Maximum width of sparkline

    Returns:
        ASCII sparkline string
    """
```

#### Single Responsibility

Each function does one thing well:

- `generate_sparkline()`: Only generates sparklines
- `sanitize_text()`: Only sanitizes text
- `format_currency()`: Only formats currency

### 3. **Error Handling**

#### Custom Exception Hierarchy

```
TerminalCoinException (base)
├── APIException
│   ├── RateLimitException
│   └── DataNotFoundException
├── NetworkException
├── ValidationException
├── ParsingException
└── ConfigurationException
```

#### Graceful Degradation

- API failures don't crash the app
- Missing data shows defaults
- Errors are logged but don't interrupt UX

### 4. **Security Features**

#### Input Validation

```python
@field_validator('link')
@classmethod
def validate_url(cls, v: str) -> str:
    if not v.startswith(('http://', 'https://', '#')):
        raise ValueError(f"Invalid URL format: {v}")
    return v
```

#### Rate Limiting

```python
class RateLimiter:
    def __init__(self, max_calls: int, period: int):
        self.max_calls = max_calls
        self.period = period
```

#### Text Sanitization

```python
def sanitize_text(text: str, max_length: Optional[int] = None) -> str:
    # Remove control characters
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', text)
    return sanitized.strip()
```

### 5. **Data Validation with Pydantic**

All external data is validated through Pydantic models:

```python
class CoinMarketData(BaseModel):
    id: str = Field(..., description="Coin identifier")
    symbol: str = Field(..., description="Coin symbol")
    current_price: float = Field(..., gt=0, description="Current price")

    @field_validator('symbol')
    @classmethod
    def symbol_uppercase(cls, v: str) -> str:
        return v.upper() if v else v
```

### 6. **Logging Strategy**

#### Structured Logging

```python
logger.info(f"Successfully fetched {len(coins)} coins")
logger.warning(f"Rate limit reached. Waiting {sleep_time:.2f}s")
logger.error(f"Failed to fetch coin details: {e}")
```

#### Log Levels

- **DEBUG**: Detailed information for debugging
- **INFO**: General informational messages
- **WARNING**: Warning messages (recoverable errors)
- **ERROR**: Error messages (handled exceptions)
- **CRITICAL**: Critical errors (unrecoverable)

### 7. **Configuration Management**

#### Immutable Configuration

```python
@dataclass(frozen=True)
class APIConfig:
    COINGECKO_BASE_URL: str = "https://api.coingecko.com/api/v3"
    REQUEST_TIMEOUT: int = 10
    MAX_RETRIES: int = 3
```

#### Environment Variables

```python
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE: str = os.getenv("LOG_FILE", "terminalcoin.log")
```

## Design Patterns Used

### 1. **Singleton Pattern**

```python
_news_client_instance: Optional[NewsClient] = None

def get_news_client() -> NewsClient:
    global _news_client_instance
    if _news_client_instance is None:
        _news_client_instance = NewsClient()
    return _news_client_instance
```

### 2. **Decorator Pattern**

```python
class RateLimiter:
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            self._wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
```

### 3. **Strategy Pattern**

Different sentiment analysis strategies can be swapped:

```python
class SentimentAnalyzer:
    def analyze(self, text: str) -> SentimentType:
        # Current: VADER sentiment
        # Could be swapped with other analyzers
```

### 4. **Factory Pattern**

```python
def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    # Creates and configures logger instances
```

## Code Quality Metrics

### Complexity

- Maximum cyclomatic complexity: 10
- Average function length: < 30 lines
- Maximum file length: < 500 lines

### Test Coverage Goals

- Unit tests: > 80%
- Integration tests: > 60%
- Critical paths: 100%

### Documentation

- All public APIs documented
- All modules have docstrings
- README with usage examples
- Security policy documented

## Future Improvements

1. **Caching Layer**: Add Redis/SQLite caching for API responses
2. **Async/Await**: Convert to async for better performance
3. **Plugin System**: Allow custom data sources
4. **Configuration UI**: In-app configuration editor
5. **Export Features**: Export data to CSV/JSON
6. **Alerts**: Price alerts and notifications
7. **Historical Data**: Charts and historical analysis

## Contributing Guidelines

1. **Code Style**: Follow PEP 8
2. **Type Hints**: Required for all functions
3. **Docstrings**: Required for all public APIs
4. **Tests**: Required for new features
5. **Security**: Follow SECURITY.md guidelines
6. **Logging**: Use appropriate log levels
7. **Error Handling**: Use custom exceptions

## Performance Considerations

1. **Rate Limiting**: Prevents API abuse
2. **Connection Pooling**: Reuses HTTP connections
3. **Lazy Loading**: Data loaded on demand
4. **Efficient Rendering**: Minimal UI updates
5. **Memory Management**: No data hoarding

## Security Considerations

1. **No Credentials**: Uses public APIs only
2. **Input Validation**: All inputs validated
3. **Output Sanitization**: All outputs sanitized
4. **HTTPS Only**: Secure connections only
5. **No Code Injection**: No eval/exec usage
6. **Dependency Security**: Regular updates
