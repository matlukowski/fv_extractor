"""Unit tests for InvoiceData model (RED phase - tests first)"""
import pytest
import pandas as pd
from datetime import date
from pydantic import ValidationError
from src.models.invoice_data import InvoiceData
from src.models.invoice_item import InvoiceItem


@pytest.fixture
def valid_invoice_dict():
    """Fixture with valid invoice data"""
    return {
        "invoice_number": "FV001/2025",
        "issue_date": date(2025, 1, 15),
        "seller_name": "ACME Corp Sp. z o.o.",
        "seller_nip": "1234567890",
        "buyer_name": "XYZ Solutions",
        "items": [
            {
                "description": "Laptop",
                "quantity": 2.0,
                "unit_price_net": 4000.0,
                "vat_rate": 23,
                "total_gross": 9840.0,
                "category": "IT"
            },
            {
                "description": "Mouse",
                "quantity": 2.0,
                "unit_price_net": 50.0,
                "vat_rate": 23,
                "total_gross": 123.0,
                "category": "IT"
            }
        ],
        "total_net_sum": 8100.0,
        "total_gross_sum": 9963.0,
        "currency": "PLN"
    }


class TestInvoiceDataCreation:
    """Test InvoiceData model creation"""

    def test_invoice_data_valid_creation(self, valid_invoice_dict):
        """Should create InvoiceData with valid complete data"""
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.invoice_number == "FV001/2025"
        assert invoice.issue_date == date(2025, 1, 15)
        assert invoice.seller_name == "ACME Corp Sp. z o.o."
        assert invoice.seller_nip == "1234567890"
        assert invoice.buyer_name == "XYZ Solutions"
        assert len(invoice.items) == 2
        assert invoice.total_net_sum == 8100.0
        assert invoice.total_gross_sum == 9963.0
        assert invoice.currency == "PLN"

    def test_invoice_data_creates_invoice_item_objects(self, valid_invoice_dict):
        """Should convert item dicts to InvoiceItem objects"""
        invoice = InvoiceData(**valid_invoice_dict)

        assert all(isinstance(item, InvoiceItem) for item in invoice.items)
        assert invoice.items[0].description == "Laptop"
        assert invoice.items[1].description == "Mouse"


class TestInvoiceDataNIPNormalization:
    """Test NIP normalization in InvoiceData"""

    def test_invoice_data_normalizes_nip(self, valid_invoice_dict):
        """Should normalize NIP with spaces and dashes"""
        valid_invoice_dict["seller_nip"] = "PL 123-456-78-90"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.seller_nip == "1234567890"

    def test_invoice_data_normalizes_nip_with_dots(self, valid_invoice_dict):
        """Should normalize NIP with dots"""
        valid_invoice_dict["seller_nip"] = "123.456.78.90"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.seller_nip == "1234567890"

    def test_invoice_data_rejects_invalid_nip(self, valid_invoice_dict):
        """Should reject NIP that doesn't normalize to 10 digits"""
        valid_invoice_dict["seller_nip"] = "123456789"  # 9 digits

        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(**valid_invoice_dict)

        assert "seller_nip" in str(exc_info.value).lower()


class TestInvoiceDataInvoiceNumberNormalization:
    """Test invoice number normalization"""

    def test_invoice_data_normalizes_invoice_number(self, valid_invoice_dict):
        """Should remove spaces from invoice number"""
        valid_invoice_dict["invoice_number"] = "FV 001 / 2025"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.invoice_number == "FV001/2025"

    def test_invoice_data_strips_invoice_number(self, valid_invoice_dict):
        """Should strip leading/trailing spaces from invoice number"""
        valid_invoice_dict["invoice_number"] = "  FV001/2025  "
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.invoice_number == "FV001/2025"

    def test_invoice_data_rejects_empty_invoice_number(self, valid_invoice_dict):
        """Should reject empty invoice number"""
        valid_invoice_dict["invoice_number"] = "   "

        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(**valid_invoice_dict)

        assert "invoice_number" in str(exc_info.value).lower()


class TestInvoiceDataDateParsing:
    """Test date parsing from various formats"""

    def test_invoice_data_parses_date_string_dots(self, valid_invoice_dict):
        """Should parse DD.MM.YYYY format"""
        valid_invoice_dict["issue_date"] = "15.01.2025"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.issue_date == date(2025, 1, 15)

    def test_invoice_data_parses_date_string_slash(self, valid_invoice_dict):
        """Should parse DD/MM/YYYY format"""
        valid_invoice_dict["issue_date"] = "15/01/2025"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.issue_date == date(2025, 1, 15)

    def test_invoice_data_parses_iso_date_string(self, valid_invoice_dict):
        """Should parse YYYY-MM-DD format"""
        valid_invoice_dict["issue_date"] = "2025-01-15"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.issue_date == date(2025, 1, 15)

    def test_invoice_data_accepts_date_object(self, valid_invoice_dict):
        """Should accept date objects directly"""
        valid_invoice_dict["issue_date"] = date(2025, 1, 15)
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.issue_date == date(2025, 1, 15)

    def test_invoice_data_rejects_invalid_date(self, valid_invoice_dict):
        """Should reject invalid date strings"""
        valid_invoice_dict["issue_date"] = "invalid-date"

        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(**valid_invoice_dict)

        assert "issue_date" in str(exc_info.value).lower()


class TestInvoiceDataItemsValidation:
    """Test items array validation"""

    def test_invoice_data_requires_at_least_one_item(self, valid_invoice_dict):
        """Should reject invoice with empty items array"""
        valid_invoice_dict["items"] = []

        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(**valid_invoice_dict)

        assert "items" in str(exc_info.value).lower()

    def test_invoice_data_accepts_single_item(self, valid_invoice_dict):
        """Should accept invoice with single item"""
        valid_invoice_dict["items"] = [valid_invoice_dict["items"][0]]
        invoice = InvoiceData(**valid_invoice_dict)

        assert len(invoice.items) == 1

    def test_invoice_data_accepts_many_items(self, valid_invoice_dict):
        """Should accept invoice with many items"""
        item = valid_invoice_dict["items"][0].copy()
        valid_invoice_dict["items"] = [item for _ in range(10)]
        invoice = InvoiceData(**valid_invoice_dict)

        assert len(invoice.items) == 10


class TestInvoiceDataCurrencyValidation:
    """Test currency code validation"""

    def test_invoice_data_accepts_pln(self, valid_invoice_dict):
        """Should accept PLN currency"""
        valid_invoice_dict["currency"] = "PLN"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.currency == "PLN"

    def test_invoice_data_accepts_eur(self, valid_invoice_dict):
        """Should accept EUR currency"""
        valid_invoice_dict["currency"] = "EUR"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.currency == "EUR"

    def test_invoice_data_accepts_usd(self, valid_invoice_dict):
        """Should accept USD currency"""
        valid_invoice_dict["currency"] = "USD"
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.currency == "USD"

    def test_invoice_data_defaults_to_pln(self, valid_invoice_dict):
        """Should default currency to PLN if not provided"""
        del valid_invoice_dict["currency"]
        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.currency == "PLN"


class TestInvoiceDataToDataFrame:
    """Test conversion to pandas DataFrame"""

    def test_invoice_data_to_dataframe_conversion(self, valid_invoice_dict):
        """Should convert to DataFrame with correct structure"""
        invoice = InvoiceData(**valid_invoice_dict)
        df = invoice.to_dataframe()

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2  # 2 items

    def test_invoice_data_to_dataframe_includes_header_fields(self, valid_invoice_dict):
        """Should include header fields in DataFrame"""
        invoice = InvoiceData(**valid_invoice_dict)
        df = invoice.to_dataframe()

        # Header fields should be in columns or as metadata
        assert "invoice_number" in df.columns or all(df.get("invoice_number") == "FV001/2025")

    def test_invoice_data_to_dataframe_includes_item_fields(self, valid_invoice_dict):
        """Should include all item fields in DataFrame"""
        invoice = InvoiceData(**valid_invoice_dict)
        df = invoice.to_dataframe()

        # Item fields should be present
        required_columns = ["description", "quantity", "unit_price_net", "vat_rate", "total_gross"]
        for col in required_columns:
            assert col in df.columns

    def test_invoice_data_to_dataframe_correct_values(self, valid_invoice_dict):
        """Should have correct values in DataFrame"""
        invoice = InvoiceData(**valid_invoice_dict)
        df = invoice.to_dataframe()

        # Check first row values
        assert df.iloc[0]["description"] == "Laptop"
        assert df.iloc[0]["quantity"] == 2.0
        assert df.iloc[1]["description"] == "Mouse"


class TestInvoiceDataEdgeCases:
    """Test edge cases"""

    def test_invoice_data_accepts_zero_net_sum(self, valid_invoice_dict):
        """Should accept zero net sum (free invoice)"""
        valid_invoice_dict["items"][0]["unit_price_net"] = 0.0
        valid_invoice_dict["items"][0]["total_gross"] = 0.0
        valid_invoice_dict["items"][1]["unit_price_net"] = 0.0
        valid_invoice_dict["items"][1]["total_gross"] = 0.0
        valid_invoice_dict["total_net_sum"] = 0.0
        valid_invoice_dict["total_gross_sum"] = 0.0

        invoice = InvoiceData(**valid_invoice_dict)

        assert invoice.total_net_sum == 0.0
        assert invoice.total_gross_sum == 0.0

    def test_invoice_data_rejects_negative_total_net(self, valid_invoice_dict):
        """Should reject negative total_net_sum"""
        valid_invoice_dict["total_net_sum"] = -100.0

        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(**valid_invoice_dict)

        assert "total_net_sum" in str(exc_info.value).lower()

    def test_invoice_data_rejects_negative_total_gross(self, valid_invoice_dict):
        """Should reject negative total_gross_sum"""
        valid_invoice_dict["total_gross_sum"] = -100.0

        with pytest.raises(ValidationError) as exc_info:
            InvoiceData(**valid_invoice_dict)

        assert "total_gross_sum" in str(exc_info.value).lower()
