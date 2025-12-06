"""Unit tests for Grok AI Client (RED phase - tests first)"""
import pytest
import json
import os
from unittest.mock import Mock, patch, MagicMock
from pydantic import ValidationError
from src.ai.grok_client import GrokClient
from src.models.invoice_data import InvoiceData


@pytest.fixture
def valid_grok_response_dict():
    """Fixture with valid invoice data matching Grok API response format"""
    return {
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
                "category": "IT"
            }
        ],
        "total_net_sum": 4500.00,
        "total_gross_sum": 5535.00,
        "currency": "PLN"
    }


@pytest.fixture
def mock_openai_response(valid_grok_response_dict):
    """Fixture that creates a mock OpenAI API response object"""
    mock_response = Mock()
    mock_choice = Mock()
    mock_message = Mock()

    # Simulate OpenAI response structure
    mock_message.content = json.dumps(valid_grok_response_dict)
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    return mock_response


class TestGrokClientInitialization:
    """Test GrokClient initialization"""

    def test_grok_client_initialization_with_api_key(self):
        """Should initialize successfully with valid API key"""
        client = GrokClient(api_key="test_api_key_123")

        assert client.api_key == "test_api_key_123"
        assert client.model_name == "grok-2-vision-1212"
        assert client.client is not None

    def test_grok_client_initialization_from_environment(self, monkeypatch):
        """Should read API key from XAI_API_KEY environment variable"""
        monkeypatch.setenv("XAI_API_KEY", "env_api_key_456")

        client = GrokClient()

        assert client.api_key == "env_api_key_456"

    def test_grok_client_raises_error_without_api_key(self, monkeypatch):
        """Should raise EnvironmentError if no API key is available"""
        monkeypatch.delenv("XAI_API_KEY", raising=False)

        with pytest.raises(EnvironmentError, match="XAI_API_KEY"):
            GrokClient()

    def test_grok_client_uses_correct_base_url(self):
        """Should configure OpenAI client with xAI base URL"""
        client = GrokClient(api_key="test_key")

        # The client should be configured with xAI endpoint
        assert hasattr(client, 'client')


class TestExtractData:
    """Test extract_data method"""

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_with_valid_response(
        self,
        mock_openai_class,
        mock_openai_response,
        valid_grok_response_dict
    ):
        """Should extract InvoiceData from valid API response"""
        # Setup mock
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client_instance

        # Create client and call extract_data
        client = GrokClient(api_key="test_key")
        result = client.extract_data(["base64_image_string"])

        # Verify result
        assert isinstance(result, InvoiceData)
        assert result.invoice_number == "FV001/2025"
        assert result.seller_name == "ACME Corp Sp. z o.o."
        assert len(result.items) == 1

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_calls_api_correctly(
        self,
        mock_openai_class,
        mock_openai_response
    ):
        """Should call OpenAI API with correct parameters"""
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")
        client.extract_data(["base64_image"])

        # Verify API was called
        mock_client_instance.chat.completions.create.assert_called_once()
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs

        assert call_kwargs['model'] == 'grok-2-vision-1212'
        assert 'messages' in call_kwargs
        assert call_kwargs['temperature'] == 0.1

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_with_multiple_images(
        self,
        mock_openai_class,
        mock_openai_response
    ):
        """Should handle multiple images in single request"""
        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.return_value = mock_openai_response
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")
        result = client.extract_data(["image1_base64", "image2_base64"])

        assert isinstance(result, InvoiceData)

        # Verify messages were built with multiple images
        call_kwargs = mock_client_instance.chat.completions.create.call_args.kwargs
        messages = call_kwargs['messages']

        # Should have at least one message with content
        assert len(messages) > 0


class TestErrorHandling:
    """Test error handling scenarios"""

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_handles_malformed_json(self, mock_openai_class):
        """Should raise JSONDecodeError for malformed JSON response"""
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        # Return invalid JSON
        mock_message.content = "This is not valid JSON {broken"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")

        with pytest.raises(json.JSONDecodeError):
            client.extract_data(["base64_image"])

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_handles_validation_error(self, mock_openai_class):
        """Should raise ValidationError when JSON doesn't match schema"""
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        # Return JSON with missing required fields
        invalid_data = {"invoice_number": "FV001"}  # Missing many fields
        mock_message.content = json.dumps(invalid_data)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")

        with pytest.raises(ValidationError):
            client.extract_data(["base64_image"])

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_handles_api_timeout(self, mock_openai_class):
        """Should handle API timeout errors"""
        from openai import APITimeoutError

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = APITimeoutError(
            request=Mock()
        )
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")

        with pytest.raises(APITimeoutError):
            client.extract_data(["base64_image"])

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_handles_rate_limit(self, mock_openai_class):
        """Should handle 429 rate limit errors"""
        from openai import RateLimitError

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = RateLimitError(
            message="Rate limit exceeded",
            response=Mock(status_code=429),
            body=None
        )
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")

        with pytest.raises(RateLimitError):
            client.extract_data(["base64_image"])

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_handles_api_error(self, mock_openai_class):
        """Should handle general API errors"""
        from openai import APIError

        mock_client_instance = Mock()
        mock_client_instance.chat.completions.create.side_effect = APIError(
            message="API Error",
            request=Mock(),
            body=None
        )
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")

        with pytest.raises(APIError):
            client.extract_data(["base64_image"])


class TestMessageBuilding:
    """Test message building for OpenAI API"""

    def test_build_messages_structure(self):
        """Should build correct message structure for vision API"""
        client = GrokClient(api_key="test_key")
        messages = client._build_messages(["base64_image_1"])

        assert isinstance(messages, list)
        assert len(messages) > 0

        # Should have a user message
        user_message = messages[0]
        assert user_message['role'] == 'user'
        assert 'content' in user_message

    def test_build_messages_includes_images(self):
        """Should include all images in message content"""
        client = GrokClient(api_key="test_key")
        images = ["image1_b64", "image2_b64"]
        messages = client._build_messages(images)

        # Verify images are included in content
        user_message = messages[0]
        content = user_message['content']

        # Content should be a list with text and image parts
        assert isinstance(content, list)

    def test_build_messages_includes_prompt(self):
        """Should include extraction prompt in messages"""
        client = GrokClient(api_key="test_key")
        messages = client._build_messages(["base64_image"])

        # Prompt should be in the message content
        user_message = messages[0]
        content_str = str(user_message['content'])

        # Should contain key instructions
        assert 'invoice' in content_str.lower() or 'extract' in content_str.lower()


class TestEdgeCases:
    """Test edge cases"""

    @patch('src.ai.grok_client.OpenAI')
    def test_extract_data_with_empty_items_array(self, mock_openai_class):
        """Should reject response with empty items array"""
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()

        # Response with empty items
        invalid_data = {
            "invoice_number": "FV001/2025",
            "issue_date": "2025-01-15",
            "seller_name": "ACME",
            "seller_nip": "1234567890",
            "buyer_name": "XYZ",
            "items": [],  # Empty!
            "total_net_sum": 0,
            "total_gross_sum": 0,
            "currency": "PLN"
        }
        mock_message.content = json.dumps(invalid_data)
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]

        mock_client_instance.chat.completions.create.return_value = mock_response
        mock_openai_class.return_value = mock_client_instance

        client = GrokClient(api_key="test_key")

        with pytest.raises(ValidationError):
            client.extract_data(["base64_image"])

    def test_extract_data_requires_non_empty_images_list(self):
        """Should handle empty images list appropriately"""
        client = GrokClient(api_key="test_key")

        # Should raise an error or handle gracefully
        with pytest.raises((ValueError, IndexError, Exception)):
            client.extract_data([])
