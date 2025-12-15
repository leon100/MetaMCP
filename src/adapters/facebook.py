"""Facebook Messenger adapter implementation."""

from typing import Any

import httpx

from ..errors import ErrorCode, MetaMCPError, map_meta_api_error
from ..logging_config import logger
from .base import BasePlatformAdapter


class FacebookAdapter(BasePlatformAdapter):
    """Facebook Messenger platform adapter."""

    def __init__(self, access_token: str, api_version: str = "v21.0", **kwargs: Any) -> None:
        super().__init__(access_token, **kwargs)
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"

    async def send_message(
        self, recipient_id: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Send a Facebook Messenger message."""
        url = f"{self.base_url}/me/messages"
        payload: dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "message": {"text": content},
        }

        if media_url:
            payload["message"] = {
                "attachment": {"type": "image", "payload": {"url": media_url, "is_reusable": True}}
            }
            if content:
                # Send text separately if media is included
                payload["message"]["text"] = content

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, params={"access_token": self.access_token}, json=payload, timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Sent Facebook message", extra={"recipient_id": recipient_id})
                return {"message_id": data.get("message_id")}
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                logger.error(
                    f"Facebook API error: {e.response.status_code}",
                    extra={"status": e.response.status_code, "response": e.response.text},
                )
                raise MetaMCPError(error_code, str(e))

    async def get_messages(
        self, conversation_id: str | None = None, recipient_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Retrieve Facebook Messenger messages."""
        if not conversation_id:
            # If only recipient_id provided, we'd need to get conversation first
            # For simplicity, raise error - in real implementation would query conversations API
            raise MetaMCPError(
                ErrorCode.MISSING_IDENTIFIER,
                "conversation_id is required for Facebook messages",
            )

        url = f"{self.base_url}/{conversation_id}/messages"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    params={"access_token": self.access_token, "limit": limit},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get("data", [])  # type: ignore
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                raise MetaMCPError(error_code, str(e))

    async def post_content(
        self,
        content: str | None = None,
        media_urls: list[str] | None = None,
        target_id: str | None = None,
    ) -> dict[str, Any]:
        """Post to Facebook Page feed."""
        page_id = target_id or "me"
        url = f"{self.base_url}/{page_id}/feed"

        payload: dict[str, Any] = {}
        if content:
            payload["message"] = content
        if media_urls and media_urls[0]:
            payload["link"] = media_urls[0]

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, params={"access_token": self.access_token}, json=payload, timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Posted to Facebook feed", extra={"page_id": page_id})
                return {"post_id": data.get("id")}
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                raise MetaMCPError(error_code, str(e))

    async def get_analytics(self, metric: str, period: str = "day") -> dict[str, Any]:
        """Get Facebook Page insights."""
        url = f"{self.base_url}/me/insights/{metric}"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    params={"access_token": self.access_token, "period": period},
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return {"metric": metric, "period": period, "data": data.get("data", [])}
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                raise MetaMCPError(error_code, str(e))
