"""Unit tests for InvoiceItem model (RED phase - tests first)"""
import pytest
from pydantic import ValidationError
from src.models.invoice_item import InvoiceItem


class TestInvoiceItemCreation:
    """Test InvoiceItem model creation and validation"""

    def test_invoice_item_valid_creation(self):
        """Should create InvoiceItem with all valid fields"""
        item = InvoiceItem(
            description="Laptop Dell XPS 15",
            quantity=2.0,
            unit_price_net=4500.00,
            vat_rate=23,
            total_gross=11070.00,
            category="IT Equipment"
        )

        assert item.description == "Laptop Dell XPS 15"
        assert item.quantity == 2.0
        assert item.unit_price_net == 4500.00
        assert item.vat_rate == 23
        assert item.total_gross == 11070.00
        assert item.category == "IT Equipment"

    def test_invoice_item_default_quantity_is_one(self):
        """Should default quantity to 1.0 if not provided"""
        item = InvoiceItem(
            description="Service",
            unit_price_net=100.0,
            vat_rate=23,
            total_gross=123.0
        )

        assert item.quantity == 1.0

    def test_invoice_item_category_optional(self):
        """Should allow category to be None"""
        item = InvoiceItem(
            description="Service",
            quantity=1.0,
            unit_price_net=100.0,
            vat_rate=23,
            total_gross=123.0
        )

        assert item.category is None

    def test_invoice_item_with_category_none(self):
        """Should accept explicit None for category"""
        item = InvoiceItem(
            description="Service",
            quantity=1.0,
            unit_price_net=100.0,
            vat_rate=23,
            total_gross=123.0,
            category=None
        )

        assert item.category is None


class TestInvoiceItemValidation:
    """Test InvoiceItem validation rules"""

    def test_invoice_item_negative_quantity_raises_error(self):
        """Should reject negative quantity"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="Product",
                quantity=-5.0,
                unit_price_net=100.0,
                vat_rate=23,
                total_gross=123.0
            )

        assert "quantity" in str(exc_info.value).lower()

    def test_invoice_item_zero_quantity_raises_error(self):
        """Should reject zero quantity"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="Product",
                quantity=0.0,
                unit_price_net=100.0,
                vat_rate=23,
                total_gross=123.0
            )

        assert "quantity" in str(exc_info.value).lower()

    def test_invoice_item_negative_unit_price_raises_error(self):
        """Should reject negative unit price"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="Product",
                quantity=1.0,
                unit_price_net=-100.0,
                vat_rate=23,
                total_gross=123.0
            )

        assert "unit_price_net" in str(exc_info.value).lower()

    def test_invoice_item_negative_vat_rate_raises_error(self):
        """Should reject negative VAT rate"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="Product",
                quantity=1.0,
                unit_price_net=100.0,
                vat_rate=-1,
                total_gross=123.0
            )

        assert "vat_rate" in str(exc_info.value).lower()

    def test_invoice_item_vat_rate_over_100_raises_error(self):
        """Should reject VAT rate over 100%"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="Product",
                quantity=1.0,
                unit_price_net=100.0,
                vat_rate=101,
                total_gross=123.0
            )

        assert "vat_rate" in str(exc_info.value).lower()

    def test_invoice_item_empty_description_raises_error(self):
        """Should reject empty description"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="",
                quantity=1.0,
                unit_price_net=100.0,
                vat_rate=23,
                total_gross=123.0
            )

        assert "description" in str(exc_info.value).lower()

    def test_invoice_item_whitespace_description_raises_error(self):
        """Should reject whitespace-only description"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="   ",
                quantity=1.0,
                unit_price_net=100.0,
                vat_rate=23,
                total_gross=123.0
            )

        assert "description" in str(exc_info.value).lower()

    def test_invoice_item_negative_total_gross_raises_error(self):
        """Should reject negative total gross"""
        with pytest.raises(ValidationError) as exc_info:
            InvoiceItem(
                description="Product",
                quantity=1.0,
                unit_price_net=100.0,
                vat_rate=23,
                total_gross=-123.0
            )

        assert "total_gross" in str(exc_info.value).lower()


class TestInvoiceItemSerialization:
    """Test InvoiceItem serialization"""

    def test_invoice_item_serialization_to_dict(self):
        """Should serialize to dict correctly"""
        item = InvoiceItem(
            description="Laptop",
            quantity=2.0,
            unit_price_net=4500.00,
            vat_rate=23,
            total_gross=11070.00,
            category="IT"
        )

        item_dict = item.model_dump()

        assert item_dict["description"] == "Laptop"
        assert item_dict["quantity"] == 2.0
        assert item_dict["unit_price_net"] == 4500.00
        assert item_dict["vat_rate"] == 23
        assert item_dict["total_gross"] == 11070.00
        assert item_dict["category"] == "IT"

    def test_invoice_item_serialization_with_none_category(self):
        """Should serialize with None category"""
        item = InvoiceItem(
            description="Service",
            quantity=1.0,
            unit_price_net=100.0,
            vat_rate=23,
            total_gross=123.0
        )

        item_dict = item.model_dump()
        assert item_dict["category"] is None


class TestInvoiceItemEdgeCases:
    """Test edge cases for InvoiceItem"""

    def test_invoice_item_strips_description(self):
        """Should strip whitespace from description"""
        item = InvoiceItem(
            description="  Laptop  ",
            quantity=1.0,
            unit_price_net=100.0,
            vat_rate=23,
            total_gross=123.0
        )

        assert item.description == "Laptop"

    def test_invoice_item_accepts_zero_vat(self):
        """Should accept 0% VAT (VAT-exempt products)"""
        item = InvoiceItem(
            description="Book",
            quantity=1.0,
            unit_price_net=50.0,
            vat_rate=0,
            total_gross=50.0
        )

        assert item.vat_rate == 0

    def test_invoice_item_accepts_fractional_quantity(self):
        """Should accept fractional quantities (e.g., 0.5 kg)"""
        item = InvoiceItem(
            description="Cables (meters)",
            quantity=2.5,
            unit_price_net=10.0,
            vat_rate=23,
            total_gross=30.75
        )

        assert item.quantity == 2.5

    def test_invoice_item_accepts_zero_price(self):
        """Should accept zero price (free items)"""
        item = InvoiceItem(
            description="Free sample",
            quantity=1.0,
            unit_price_net=0.0,
            vat_rate=0,
            total_gross=0.0
        )

        assert item.unit_price_net == 0.0
        assert item.total_gross == 0.0
