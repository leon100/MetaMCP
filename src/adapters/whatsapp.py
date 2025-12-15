"""WhatsApp Business Cloud API adapter implementation."""

from typing import Any

import httpx

from ..errors import MetaMCPError, PlatformNotSupportedError, map_meta_api_error
from ..logging_config import logger
from .base import BasePlatformAdapter


class WhatsAppAdapter(BasePlatformAdapter):
    """WhatsApp Business Cloud API adapter."""

    def __init__(
        self, access_token: str, phone_number_id: str, api_version: str = "v21.0", **kwargs: Any
    ) -> None:
        super().__init__(access_token, **kwargs)
        self.phone_number_id = phone_number_id
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"

    async def send_message(
        self, recipient_id: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Send a WhatsApp message."""
        url = f"{self.base_url}/{self.phone_number_id}/messages"

        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": recipient_id,
            "type": "text",
            "text": {"body": content},
        }

        if media_url:
            # Determine media type (simplified - assumes image)
            payload["type"] = "image"
            payload["image"] = {"link": media_url}
            del payload["text"]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, params={"access_token": self.access_token}, json=payload, timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Sent WhatsApp message", extra={"recipient": recipient_id})
                # WhatsApp returns messages array with IDs
                messages = data.get("messages", [])
                message_id = messages[0]["id"] if messages else "unknown"
                return {"message_id": message_id}
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                logger.error(
                    f"WhatsApp API error: {e.response.status_code}",
                    extra={"status": e.response.status_code},
                )
                raise MetaMCPError(error_code, str(e))

    async def get_messages(
        self, conversation_id: str | None = None, recipient_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Retrieve WhatsApp messages - NOT SUPPORTED.

        WhatsApp Cloud API is webhook-based and does not provide
        a message history retrieval endpoint.
        """
        raise PlatformNotSupportedError("whatsapp", "get_messages")

    async def post_content(
        self,
        content: str | None = None,
        media_urls: list[str] | None = None,
        target_id: str | None = None,
    ) -> dict[str, Any]:
        """Post content - NOT SUPPORTED on WhatsApp."""
        raise PlatformNotSupportedError("whatsapp", "post_content")

    async def get_analytics(self, metric: str, period: str = "day") -> dict[str, Any]:
        """Get analytics - NOT SUPPORTED on WhatsApp."""
        raise PlatformNotSupportedError("whatsapp", "get_analytics")
