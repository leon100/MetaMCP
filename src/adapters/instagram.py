"""Instagram adapter implementation."""

from typing import Any

import httpx

from ..errors import ErrorCode, MetaMCPError, map_meta_api_error
from ..logging_config import logger
from .base import BasePlatformAdapter


class InstagramAdapter(BasePlatformAdapter):
    """Instagram platform adapter."""

    def __init__(self, access_token: str, api_version: str = "v21.0", **kwargs: Any) -> None:
        super().__init__(access_token, **kwargs)
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"

    async def send_message(
        self, recipient_id: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Send an Instagram Direct message."""
        url = f"{self.base_url}/me/messages"
        payload: dict[str, Any] = {
            "recipient": {"id": recipient_id},
            "message": {"text": content},
        }

        if media_url:
            payload["message"] = {
                "attachment": {"type": "image", "payload": {"url": media_url}}
            }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    url, params={"access_token": self.access_token}, json=payload, timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Sent Instagram message", extra={"recipient_id": recipient_id})
                return {"message_id": data.get("message_id")}
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                logger.error(
                    f"Instagram API error: {e.response.status_code}",
                    extra={"status": e.response.status_code},
                )
                raise MetaMCPError(error_code, str(e))

    async def get_messages(
        self, conversation_id: str | None = None, recipient_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Retrieve Instagram Direct messages."""
        if not conversation_id:
            raise MetaMCPError(
                ErrorCode.MISSING_IDENTIFIER,
                "conversation_id is required for Instagram messages",
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
        """Post media to Instagram feed (requires media container creation)."""
        if not media_urls or not media_urls[0]:
            raise MetaMCPError(
                ErrorCode.MISSING_CONTENT, "Instagram posts require media_urls"
            )

        ig_user_id = target_id or "me"

        # Step 1: Create media container
        container_url = f"{self.base_url}/{ig_user_id}/media"
        container_payload = {
            "image_url": media_urls[0],
            "caption": content or "",
        }

        async with httpx.AsyncClient() as client:
            try:
                # Create container
                response = await client.post(
                    container_url,
                    params={"access_token": self.access_token},
                    json=container_payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                container_data = response.json()
                container_id = container_data.get("id")

                # Step 2: Publish container
                publish_url = f"{self.base_url}/{ig_user_id}/media_publish"
                publish_payload = {"creation_id": container_id}

                response = await client.post(
                    publish_url,
                    params={"access_token": self.access_token},
                    json=publish_payload,
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                logger.info("Posted to Instagram feed", extra={"ig_user_id": ig_user_id})
                return {"post_id": data.get("id")}

            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                raise MetaMCPError(error_code, str(e))

    async def get_analytics(self, metric: str, period: str = "day") -> dict[str, Any]:
        """Get Instagram insights."""
        url = f"{self.base_url}/me/insights"

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    params={
                        "access_token": self.access_token,
                        "metric": metric,
                        "period": period,
                    },
                    timeout=30.0,
                )
                response.raise_for_status()
                data = response.json()
                return {"metric": metric, "period": period, "data": data.get("data", [])}
            except httpx.HTTPStatusError as e:
                error_code = map_meta_api_error(e.response.status_code, e.response.json())
                raise MetaMCPError(error_code, str(e))
