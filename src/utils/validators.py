"""Validators for invoice data normalization and parsing"""
import re
from datetime import date, datetime
from typing import Union


def normalize_nip(nip: str) -> str:
    """
    Normalize Polish NIP (tax identification number) to 10 digits.

    Args:
        nip: NIP string (may contain PL prefix, dashes, spaces, dots)

    Returns:
        Normalized 10-digit NIP

    Raises:
        ValueError: If normalized NIP doesn't have exactly 10 digits

    Examples:
        >>> normalize_nip("PL 123-456-78-90")
        '1234567890'
        >>> normalize_nip("123 456 78 90")
        '1234567890'
    """
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', nip)

    # Validate length
    if len(digits_only) != 10:
        raise ValueError(
            f"NIP musi zawierać dokładnie 10 cyfr, otrzymano {len(digits_only)}"
        )

    return digits_only


def parse_polish_date(date_str: Union[str, date]) -> date:
    """
    Parse Polish date formats to datetime.date object.

    Supports formats:
    - DD.MM.YYYY (Polish standard)
    - DD/MM/YYYY
    - YYYY-MM-DD (ISO)
    - date objects (pass through)

    Args:
        date_str: Date string or date object

    Returns:
        datetime.date object

    Raises:
        ValueError: If date string cannot be parsed

    Examples:
        >>> parse_polish_date("12.01.2025")
        date(2025, 1, 12)
        >>> parse_polish_date("2025-01-12")
        date(2025, 1, 12)
    """
    # If already a date object, return as-is
    if isinstance(date_str, date):
        return date_str

    # Try various date formats
    formats = [
        '%d.%m.%Y',   # DD.MM.YYYY
        '%d/%m/%Y',   # DD/MM/YYYY
        '%Y-%m-%d',   # YYYY-MM-DD (ISO)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    # If no format matched, raise error
    raise ValueError(
        f"Nie można sparsować daty: '{date_str}'. "
        f"Obsługiwane formaty: DD.MM.YYYY, DD/MM/YYYY, YYYY-MM-DD"
    )


def normalize_invoice_number(invoice_num: str) -> str:
    """
    Normalize invoice number by removing spaces.

    Args:
        invoice_num: Invoice number string

    Returns:
        Normalized invoice number (no spaces)

    Raises:
        ValueError: If invoice number is empty

    Examples:
        >>> normalize_invoice_number("FV 123 / 2025")
        'FV123/2025'
        >>> normalize_invoice_number("  FV001/2025  ")
        'FV001/2025'
    """
    # Remove all spaces and strip
    normalized = invoice_num.replace(' ', '').strip()

    # Validate not empty
    if not normalized:
        raise ValueError("Numer faktury nie może być pusty")

    return normalized
