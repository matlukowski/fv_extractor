"""InvoiceItem data model - represents a single line item on an invoice"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class InvoiceItem(BaseModel):
    """
    Single line item on an invoice.

    Represents a product or service with quantity, pricing, and VAT information.
    """

    description: str = Field(
        ...,
        min_length=1,
        description="Name/description of the product or service"
    )

    quantity: float = Field(
        default=1.0,
        gt=0,
        description="Quantity of items"
    )

    unit_price_net: float = Field(
        ...,
        ge=0,
        description="Unit price excluding VAT"
    )

    vat_rate: int = Field(
        ...,
        ge=0,
        le=100,
        description="VAT rate as percentage (e.g., 23 for 23%)"
    )

    total_gross: float = Field(
        ...,
        ge=0,
        description="Total gross amount for this line item"
    )

    category: Optional[str] = Field(
        default=None,
        description="Cost category (e.g., 'Paliwo', 'Biuro', 'IT')"
    )

    @field_validator('description')
    @classmethod
    def description_not_empty(cls, v: str) -> str:
        """Validate description is not empty or whitespace-only"""
        if not v or not v.strip():
            raise ValueError("Opis pozycji nie może być pusty")
        return v.strip()

    model_config = {
        "json_schema_extra": {
            "example": {
                "description": "Laptop Dell XPS 15",
                "quantity": 1.0,
                "unit_price_net": 4500.00,
                "vat_rate": 23,
                "total_gross": 5535.00,
                "category": "IT Equipment"
            }
        }
    }
