"""Tests for validator functions."""

import pytest

from src.errors import ValidationError
from src.validators import (
    validate_e164_phone,
    validate_get_messages_request,
    validate_post_content_request,
    validate_url,
    validate_whatsapp_recipient,
)


class TestPhoneValidation:
    """Test E.164 phone number validation."""

    def test_valid_phone_numbers(self):
        """Test valid E.164 format."""
        assert validate_e164_phone("+380991234567") is True
        assert validate_e164_phone("+1234567890") is True
        assert validate_e164_phone("+447911123456") is True

    def test_invalid_phone_numbers(self):
        """Test invalid formats."""
        assert validate_e164_phone("380991234567") is False  # Missing +
        assert validate_e164_phone("+0991234567") is False  # Starts with 0
        assert validate_e164_phone("invalid") is False
        assert validate_e164_phone("") is False

    def test_whatsapp_recipient_validation(self):
        """Test WhatsApp recipient validation."""
        # Valid
        validate_whatsapp_recipient("+380991234567")

        # Invalid
        with pytest.raises(ValidationError):
            validate_whatsapp_recipient("380991234567")


class TestURLValidation:
    """Test URL validation."""

    def test_valid_urls(self):
        """Test valid URLs."""
        validate_url("https://example.com/image.jpg")
        validate_url("http://example.com")
        # Should not raise

    def test_invalid_urls(self):
        """Test invalid URLs."""
        with pytest.raises(ValidationError):
            validate_url("not-a-url")

        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")  # Wrong protocol


class TestRequestValidation:
    """Test request validation functions."""

    def test_get_messages_requires_identifier(self):
        """Test that get_messages requires at least one ID."""
        with pytest.raises(ValidationError):
            validate_get_messages_request(None, None)

        # These should not raise
        validate_get_messages_request("conv_123", None)
        validate_get_messages_request(None, "user_456")

    def test_post_content_requires_content_or_media(self):
        """Test that post_content requires content or media."""
        with pytest.raises(ValidationError):
            validate_post_content_request("facebook", None, None)

        # Valid
        validate_post_content_request("facebook", "Hello", None)
        validate_post_content_request("facebook", None, ["https://example.com/img.jpg"])

    def test_instagram_requires_media(self):
        """Test that Instagram posts require media."""
        with pytest.raises(ValidationError):
            validate_post_content_request("instagram", "Text only", None)

        # Valid
        validate_post_content_request("instagram", "Caption", ["https://example.com/img.jpg"])
