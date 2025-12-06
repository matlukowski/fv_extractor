"""InvoiceData model - represents a complete invoice document"""
import pandas as pd
from datetime import date
from pydantic import BaseModel, Field, field_validator
from typing import List
from .invoice_item import InvoiceItem
from ..utils.validators import normalize_nip, parse_polish_date, normalize_invoice_number


class InvoiceData(BaseModel):
    """
    Complete invoice document model.

    Contains header information (seller, buyer, dates) and line items.
    All data is validated according to Polish invoice standards.
    """

    invoice_number: str = Field(
        ...,
        description="Invoice number (e.g., FV001/2025)"
    )

    issue_date: date = Field(
        ...,
        description="Invoice issue date"
    )

    seller_name: str = Field(
        ...,
        min_length=1,
        description="Seller company name"
    )

    seller_nip: str = Field(
        ...,
        description="Seller NIP (tax identification number)"
    )

    buyer_name: str = Field(
        ...,
        min_length=1,
        description="Buyer company name"
    )

    items: List[InvoiceItem] = Field(
        ...,
        min_length=1,
        description="Invoice line items"
    )

    total_net_sum: float = Field(
        ...,
        ge=0,
        description="Total net amount (sum of all items)"
    )

    total_gross_sum: float = Field(
        ...,
        ge=0,
        description="Total gross amount (total to pay)"
    )

    currency: str = Field(
        default="PLN",
        description="Currency code (PLN, EUR, USD)"
    )

    @field_validator('seller_nip')
    @classmethod
    def validate_nip(cls, v: str) -> str:
        """Normalize and validate NIP to 10 digits"""
        return normalize_nip(v)

    @field_validator('invoice_number')
    @classmethod
    def validate_invoice_number(cls, v: str) -> str:
        """Normalize invoice number (remove spaces)"""
        return normalize_invoice_number(v)

    @field_validator('issue_date', mode='before')
    @classmethod
    def parse_date(cls, v):
        """Parse date from various string formats"""
        return parse_polish_date(v)

    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert invoice data to pandas DataFrame for Excel export.

        Returns a DataFrame where each row represents one line item,
        with header fields repeated for each row.

        Returns:
            pd.DataFrame: Invoice data as tabular format
        """
        # Convert items to list of dicts
        items_data = []
        for item in self.items:
            row = {
                # Header fields (repeated for each row)
                'invoice_number': self.invoice_number,
                'issue_date': self.issue_date,
                'seller_name': self.seller_name,
                'seller_nip': self.seller_nip,
                'buyer_name': self.buyer_name,
                'currency': self.currency,
                'total_net_sum': self.total_net_sum,
                'total_gross_sum': self.total_gross_sum,

                # Item fields
                'description': item.description,
                'quantity': item.quantity,
                'unit_price_net': item.unit_price_net,
                'vat_rate': item.vat_rate,
                'total_gross': item.total_gross,
                'category': item.category,
            }
            items_data.append(row)

        return pd.DataFrame(items_data)

    model_config = {
        "json_schema_extra": {
            "example": {
                "invoice_number": "FV001/2025",
                "issue_date": "2025-01-15",
                "seller_name": "ACME Corp Sp. z o.o.",
                "seller_nip": "1234567890",
                "buyer_name": "XYZ Solutions",
                "items": [
                    {
                        "description": "Laptop Dell XPS 15",
                        "quantity": 1.0,
                        "unit_price_net": 4500.00,
                        "vat_rate": 23,
                        "total_gross": 5535.00,
                        "category": "IT Equipment"
                    }
                ],
                "total_net_sum": 4500.00,
                "total_gross_sum": 5535.00,
                "currency": "PLN"
            }
        }
    }
