"""
Unit tests for utility functions.

Run with: pytest tests/
"""

import pytest
from utils import (
    generate_sparkline,
    sanitize_text,
    format_currency,
    format_percentage,
    validate_coin_id,
    truncate_list,
    safe_get
)


class TestSparkline:
    """Tests for sparkline generation."""

    def test_generate_sparkline_basic(self):
        """Test basic sparkline generation."""
        data = [1, 2, 3, 4, 5]
        result = generate_sparkline(data, width=5)
        assert len(result) == 5
        assert isinstance(result, str)

    def test_generate_sparkline_empty(self):
        """Test sparkline with empty data."""
        result = generate_sparkline([], width=10)
        assert result == ""

    def test_generate_sparkline_flat(self):
        """Test sparkline with flat data."""
        data = [5, 5, 5, 5, 5]
        result = generate_sparkline(data, width=5)
        assert len(result) == 5
        # All characters should be the same
        assert len(set(result)) == 1

    def test_generate_sparkline_invalid_data(self):
        """Test sparkline with invalid data."""
        with pytest.raises(ValueError):
            generate_sparkline(["a", "b", "c"])


class TestTextSanitization:
    """Tests for text sanitization."""

    def test_sanitize_text_basic(self):
        """Test basic text sanitization."""
        text = "Hello World"
        result = sanitize_text(text)
        assert result == "Hello World"

    def test_sanitize_text_with_control_chars(self):
        """Test sanitization removes control characters."""
        text = "Hello\x00World\x1F"
        result = sanitize_text(text)
        assert "\x00" not in result
        assert "\x1F" not in result

    def test_sanitize_text_max_length(self):
        """Test text truncation."""
        text = "A" * 100
        result = sanitize_text(text, max_length=10)
        assert len(result) <= 13  # 10 + "..."

    def test_sanitize_text_non_string(self):
        """Test sanitization with non-string input."""
        result = sanitize_text(123)
        assert result == "123"


class TestFormatting:
    """Tests for formatting functions."""

    def test_format_currency_basic(self):
        """Test basic currency formatting."""
        result = format_currency(1234.56)
        assert result == "$1,234.56"

    def test_format_currency_no_decimals(self):
        """Test currency formatting without decimals."""
        result = format_currency(1234.56, decimals=0)
        assert result == "$1,235"

    def test_format_currency_custom_symbol(self):
        """Test currency formatting with custom symbol."""
        result = format_currency(1234.56, symbol="€")
        assert result == "€1,234.56"

    def test_format_percentage_positive(self):
        """Test percentage formatting for positive values."""
        result = format_percentage(5.67)
        assert result == "+5.67%"

    def test_format_percentage_negative(self):
        """Test percentage formatting for negative values."""
        result = format_percentage(-3.45)
        assert result == "-3.45%"


class TestValidation:
    """Tests for validation functions."""

    def test_validate_coin_id_valid(self):
        """Test validation with valid coin IDs."""
        assert validate_coin_id("bitcoin") is True
        assert validate_coin_id("ethereum") is True
        assert validate_coin_id("binance-coin") is True

    def test_validate_coin_id_invalid(self):
        """Test validation with invalid coin IDs."""
        assert validate_coin_id("Bitcoin") is False  # Uppercase
        assert validate_coin_id("bit coin") is False  # Space
        assert validate_coin_id("bit_coin") is False  # Underscore
        assert validate_coin_id("") is False  # Empty
        assert validate_coin_id(None) is False  # None


class TestUtilityFunctions:
    """Tests for other utility functions."""

    def test_truncate_list_basic(self):
        """Test basic list truncation."""
        items = [1, 2, 3, 4, 5]
        result = truncate_list(items, 3)
        assert result == [1, 2, 3]

    def test_truncate_list_no_truncation(self):
        """Test truncation when list is shorter than max."""
        items = [1, 2, 3]
        result = truncate_list(items, 10)
        assert result == [1, 2, 3]

    def test_truncate_list_invalid_input(self):
        """Test truncation with invalid input."""
        result = truncate_list("not a list", 5)
        assert result == []

    def test_safe_get_basic(self):
        """Test safe dictionary access."""
        data = {"a": {"b": {"c": 123}}}
        result = safe_get(data, "a", "b", "c")
        assert result == 123

    def test_safe_get_missing_key(self):
        """Test safe access with missing key."""
        data = {"a": {"b": 123}}
        result = safe_get(data, "a", "x", "y", default=0)
        assert result == 0

    def test_safe_get_none_value(self):
        """Test safe access with None value."""
        data = {"a": None}
        result = safe_get(data, "a", "b", default="default")
        assert result == "default"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
