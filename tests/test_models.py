"""Tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from src.models import (
    AnalyticsRequest,
    GetMessagesRequest,
    MetaError,
    MetaResponse,
    MetricType,
    Period,
    PostContentRequest,
    SendMessageRequest,
)


class TestRequestModels:
    """Test request model validation."""

    def test_send_message_request_valid(self):
        """Test valid SendMessageRequest."""
        req = SendMessageRequest(
            platform="facebook",
            recipient_id="12345",
            content="Hello",
        )
        assert req.platform == "facebook"
        assert req.content == "Hello"

    def test_send_message_requires_content(self):
        """Test that content is required and validated."""
        with pytest.raises(ValidationError):
            SendMessageRequest(
                platform="facebook",
                recipient_id="12345",
                content="",  # Empty not allowed
            )

    def test_get_messages_request_limit_validation(self):
        """Test limit constraints."""
        # Valid
        req = GetMessagesRequest(platform="instagram", limit=50)
        assert req.limit == 50

        # Too low
        with pytest.raises(ValidationError):
            GetMessagesRequest(platform="instagram", limit=0)

        # Too high
        with pytest.raises(ValidationError):
            GetMessagesRequest(platform="instagram", limit=200)

    def test_post_content_request(self):
        """Test PostContentRequest."""
        req = PostContentRequest(
            platform="facebook",
            content="Test post",
        )
        assert req.platform == "facebook"

    def test_analytics_request_enums(self):
        """Test that enums work correctly."""
        req = AnalyticsRequest(
            platform="instagram",
            metric=MetricType.REACH,
            period=Period.WEEK,
        )
        assert req.metric == MetricType.REACH
        assert req.period == Period.WEEK


class TestResponseModels:
    """Test response models."""

    def test_meta_response(self):
        """Test MetaResponse model."""
        resp = MetaResponse(
            success=True,
            platform="facebook",
            data={"message_id": "123"},
            message="Success",
        )
        assert resp.success is True
        assert resp.platform == "facebook"
        assert resp.timestamp is not None

    def test_meta_error(self):
        """Test MetaError model."""
        error = MetaError(
            error_code="AUTH_FAILED",
            error_message="Invalid token",
            platform="whatsapp",
        )
        assert error.error_code == "AUTH_FAILED"
        assert error.timestamp is not None
