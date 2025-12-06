"""Grok AI Client for invoice data extraction using xAI Vision API"""
import os
import json
from typing import List
from openai import OpenAI
from ..models.invoice_data import InvoiceData
from .prompts import INVOICE_EXTRACTION_PROMPT


class GrokClient:
    """
    AI client for extracting invoice data using Grok Vision API.

    Uses OpenAI SDK compatibility to connect to xAI's Grok model.
    Sends invoice images and receives structured JSON data.
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Grok client.

        Args:
            api_key: xAI API key. If not provided, reads from XAI_API_KEY env var.

        Raises:
            EnvironmentError: If no API key is available
        """
        self.api_key = api_key or os.getenv("XAI_API_KEY")

        if not self.api_key:
            raise EnvironmentError(
                "XAI_API_KEY not found. Please set the environment variable or pass api_key parameter."
            )

        # Initialize OpenAI client with xAI endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.x.ai/v1"
        )

        self.model_name = "grok-2-vision-1212"

    def extract_data(self, images_base64: List[str]) -> InvoiceData:
        """
        Extract invoice data from image(s).

        Args:
            images_base64: List of base64-encoded image strings

        Returns:
            Validated InvoiceData object

        Raises:
            ValueError: If images list is empty
            json.JSONDecodeError: If API returns invalid JSON
            ValidationError: If JSON doesn't match InvoiceData schema
            APITimeoutError: If API request times out
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors

        Examples:
            >>> client = GrokClient(api_key="your_key")
            >>> images = ["base64_encoded_invoice_image"]
            >>> invoice = client.extract_data(images)
            >>> print(invoice.invoice_number)
            'FV001/2025'
        """
        if not images_base64:
            raise ValueError("images_base64 list cannot be empty")

        # Build messages for API
        messages = self._build_messages(images_base64)

        # Call Grok Vision API
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=0.1,  # Low temperature for consistent extraction
            max_tokens=2000    # Enough for invoice data
        )

        # Extract response content
        content = response.choices[0].message.content

        # Parse JSON (may raise JSONDecodeError)
        data_dict = json.loads(content)

        # Validate with Pydantic (may raise ValidationError)
        invoice_data = InvoiceData(**data_dict)

        return invoice_data

    def _build_messages(self, images_base64: List[str]) -> List[dict]:
        """
        Build OpenAI-compatible message structure with images.

        Args:
            images_base64: List of base64-encoded image strings

        Returns:
            List of message dictionaries in OpenAI format

        Message structure for vision:
        [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "prompt"},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
                ]
            }
        ]
        """
        # Build content array with text prompt and images
        content = [
            {
                "type": "text",
                "text": INVOICE_EXTRACTION_PROMPT
            }
        ]

        # Add all images
        for image_b64 in images_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}"
                }
            })

        # Return message list
        return [
            {
                "role": "user",
                "content": content
            }
        ]
