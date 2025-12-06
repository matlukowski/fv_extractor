"""Unit tests for validators module (RED phase - tests written first)"""
import pytest
from datetime import date
from src.utils.validators import normalize_nip, parse_polish_date, normalize_invoice_number


class TestNormalizeNIP:
    """Test NIP (tax identification number) normalization"""

    def test_normalize_nip_removes_non_digits(self):
        """Should remove PL prefix, dashes, and spaces"""
        assert normalize_nip("PL 123-456-78-90") == "1234567890"
        assert normalize_nip("123-456-78-90") == "1234567890"
        assert normalize_nip("123 456 78 90") == "1234567890"

    def test_normalize_nip_handles_valid_input(self):
        """Should pass through already valid 10-digit NIP"""
        assert normalize_nip("1234567890") == "1234567890"

    def test_normalize_nip_raises_error_if_not_10_digits(self):
        """Should raise ValueError if not exactly 10 digits after normalization"""
        with pytest.raises(ValueError, match="10 cyfr"):
            normalize_nip("123456789")  # 9 digits

        with pytest.raises(ValueError, match="10 cyfr"):
            normalize_nip("12345678901")  # 11 digits

        with pytest.raises(ValueError, match="10 cyfr"):
            normalize_nip("")  # Empty

    def test_normalize_nip_handles_mixed_format(self):
        """Should handle various formatting styles"""
        assert normalize_nip("PL1234567890") == "1234567890"
        assert normalize_nip("123.456.78.90") == "1234567890"


class TestParsePolishDate:
    """Test date parsing from various Polish formats"""

    def test_parse_date_handles_dot_format(self):
        """Should parse DD.MM.YYYY format"""
        assert parse_polish_date("12.01.2025") == date(2025, 1, 12)
        assert parse_polish_date("31.12.2024") == date(2024, 12, 31)

    def test_parse_date_handles_slash_format(self):
        """Should parse DD/MM/YYYY format"""
        assert parse_polish_date("12/01/2025") == date(2025, 1, 12)
        assert parse_polish_date("01/06/2025") == date(2025, 6, 1)

    def test_parse_date_handles_dash_format(self):
        """Should parse YYYY-MM-DD format (ISO)"""
        assert parse_polish_date("2025-01-12") == date(2025, 1, 12)
        assert parse_polish_date("2024-12-31") == date(2024, 12, 31)

    def test_parse_date_raises_error_on_invalid(self):
        """Should raise ValueError for invalid date strings"""
        with pytest.raises(ValueError):
            parse_polish_date("invalid-date")

        with pytest.raises(ValueError):
            parse_polish_date("32.01.2025")  # Invalid day

        with pytest.raises(ValueError):
            parse_polish_date("12.13.2025")  # Invalid month

    def test_parse_date_handles_date_objects(self):
        """Should pass through date objects unchanged"""
        test_date = date(2025, 1, 12)
        assert parse_polish_date(test_date) == test_date


class TestNormalizeInvoiceNumber:
    """Test invoice number normalization"""

    def test_normalize_invoice_number_removes_spaces(self):
        """Should remove spaces from invoice number"""
        assert normalize_invoice_number("FV 123 / 2025") == "FV123/2025"
        assert normalize_invoice_number("FV 001 / 01 / 2025") == "FV001/01/2025"

    def test_normalize_invoice_number_handles_no_spaces(self):
        """Should pass through invoice numbers without spaces"""
        assert normalize_invoice_number("FV123/2025") == "FV123/2025"
        assert normalize_invoice_number("INV-2025-001") == "INV-2025-001"

    def test_normalize_invoice_number_strips_leading_trailing_spaces(self):
        """Should remove leading and trailing whitespace"""
        assert normalize_invoice_number("  FV123/2025  ") == "FV123/2025"

    def test_normalize_invoice_number_raises_error_on_empty(self):
        """Should raise ValueError for empty invoice number"""
        with pytest.raises(ValueError, match="pusty"):
            normalize_invoice_number("")

        with pytest.raises(ValueError, match="pusty"):
            normalize_invoice_number("   ")
