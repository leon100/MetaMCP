"""Tests for MetaClient and platform adapters."""

import pytest
from pytest_httpx import HTTPXMock

from src.adapters.facebook import FacebookAdapter
from src.adapters.instagram import InstagramAdapter
from src.adapters.mock import MockPlatformAdapter
from src.adapters.whatsapp import WhatsAppAdapter
from src.config import Settings
from src.errors import AuthenticationError, PlatformNotSupportedError
from src.meta_client import MetaClient


class TestMockAdapter:
    """Test mock adapter for demo mode."""

    @pytest.mark.asyncio
    async def test_send_message(self):
        """Test mock send message."""
        adapter = MockPlatformAdapter(platform="facebook")
        result = await adapter.send_message("user_123", "Hello")

        assert "message_id" in result
        assert "mock" in result["message_id"]

    @pytest.mark.asyncio
    async def test_get_messages(self):
        """Test mock get messages."""
        adapter = MockPlatformAdapter(platform="instagram")
        messages = await adapter.get_messages(limit=5)

        assert isinstance(messages, list)
        assert len(messages) <= 5

    @pytest.mark.asyncio
    async def test_post_content(self):
        """Test mock post content."""
        adapter = MockPlatformAdapter(platform="facebook")
        result = await adapter.post_content(content="Test post")

        assert "post_id" in result

    @pytest.mark.asyncio
    async def test_get_analytics(self):
        """Test mock analytics."""
        adapter = MockPlatformAdapter(platform="instagram")
        result = await adapter.get_analytics("reach", "day")

        assert "metric" in result
        assert result["metric"] == "reach"


class TestFacebookAdapter:
    """Test Facebook adapter."""

    @pytest.mark.asyncio
    async def test_send_message(self, httpx_mock: HTTPXMock):
        """Test sending Facebook message."""
        # Match URL with query params
        httpx_mock.add_response(
            method="POST",
            url="https://graph.facebook.com/v21.0/me/messages?access_token=test_token",
            json={"message_id": "msg_123"},
        )

        adapter = FacebookAdapter(access_token="test_token")
        result = await adapter.send_message("user_456", "Hello Facebook")

        assert result["message_id"] == "msg_123"


class TestWhatsAppAdapter:
    """Test WhatsApp adapter."""

    @pytest.mark.asyncio
    async def test_send_message(self, httpx_mock: HTTPXMock):
        """Test sending WhatsApp message."""
        httpx_mock.add_response(
            method="POST",
            url="https://graph.facebook.com/v21.0/12345/messages?access_token=test_token",
            json={"messages": [{"id": "wamid.123"}]},
        )

        adapter = WhatsAppAdapter(
            access_token="test_token",
            phone_number_id="12345",
        )
        result = await adapter.send_message("+380991234567", "Hello WhatsApp")

        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_get_messages_not_supported(self):
        """Test that get_messages raises error."""
        adapter = WhatsAppAdapter(
            access_token="test_token",
            phone_number_id="12345",
        )

        with pytest.raises(PlatformNotSupportedError):
            await adapter.get_messages()


class TestMetaClient:
    """Test MetaClient."""

    def test_demo_mode_returns_mock_adapter(self):
        """Test that demo mode uses mock adapter."""
        settings = Settings(demo_mode=True)
        client = MetaClient(settings)

        adapter = client.get_adapter("facebook")
        assert isinstance(adapter, MockPlatformAdapter)

    def test_missing_credentials_raises_error(self):
        """Test that missing credentials raises AuthenticationError."""
        settings = Settings(demo_mode=False, facebook_page_access_token="")
        client = MetaClient(settings)

        with pytest.raises(AuthenticationError):
            client.get_adapter("facebook")

    def test_get_facebook_adapter(self):
        """Test getting Facebook adapter."""
        settings = Settings(
            demo_mode=False,
            facebook_page_access_token="test_token",
        )
        client = MetaClient(settings)

        adapter = client.get_adapter("facebook")
        assert isinstance(adapter, FacebookAdapter)

    def test_get_instagram_adapter(self):
        """Test getting Instagram adapter."""
        settings = Settings(
            demo_mode=False,
            instagram_access_token="test_token",
        )
        client = MetaClient(settings)

        adapter = client.get_adapter("instagram")
        assert isinstance(adapter, InstagramAdapter)

    def test_get_whatsapp_adapter(self):
        """Test getting WhatsApp adapter."""
        settings = Settings(
            demo_mode=False,
            whatsapp_access_token="test_token",
            whatsapp_phone_number_id="12345",
        )
        client = MetaClient(settings)

        adapter = client.get_adapter("whatsapp")
        assert isinstance(adapter, WhatsAppAdapter)
