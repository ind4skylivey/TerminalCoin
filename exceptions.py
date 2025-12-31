"""
Custom exceptions for TerminalCoin application.

This module defines application-specific exceptions for better
error handling and debugging.
"""


class TerminalCoinException(Exception):
    """Base exception for all TerminalCoin errors."""

    def __init__(self, message: str, details: dict = None):
        """
        Initialize exception with message and optional details.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the exception."""
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class APIException(TerminalCoinException):
    """Exception raised for API-related errors."""
    pass


class NetworkException(TerminalCoinException):
    """Exception raised for network-related errors."""
    pass


class ValidationException(TerminalCoinException):
    """Exception raised for data validation errors."""
    pass


class RateLimitException(APIException):
    """Exception raised when API rate limit is exceeded."""
    pass


class DataNotFoundException(APIException):
    """Exception raised when requested data is not found."""
    pass


class ParsingException(TerminalCoinException):
    """Exception raised when data parsing fails."""
    pass


class ConfigurationException(TerminalCoinException):
    """Exception raised for configuration errors."""
    pass
