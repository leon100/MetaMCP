"""Mock adapter for testing and demo mode."""

import asyncio
from datetime import datetime, timezone
from typing import Any

from ..logging_config import logger
from .base import BasePlatformAdapter


class MockPlatformAdapter(BasePlatformAdapter):
    """Mock adapter for demo/testing without real API calls."""

    def __init__(self, access_token: str = "demo_token", platform: str = "mock", **kwargs: Any) -> None:
        super().__init__(access_token, **kwargs)
        self.platform = platform
        logger.info(f"Initialized MockPlatformAdapter for platform: {platform}")

    async def send_message(
        self, recipient_id: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """Mock send message - returns fake message ID."""
        # Simulate network delay
        await asyncio.sleep(0.1)

        message_id = f"mock_msg_{recipient_id}_{datetime.now().timestamp()}"
        logger.info(
            f"[DEMO] Sent message to {recipient_id} on {self.platform}",
            extra={"recipient_id": recipient_id, "content_length": len(content)},
        )

        return {"message_id": message_id}

    async def get_messages(
        self, conversation_id: str | None = None, recipient_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Mock get messages - returns fake message history."""
        await asyncio.sleep(0.1)

        messages = []
        for i in range(min(limit, 3)):  # Return up to 3 fake messages
            messages.append(
                {
                    "id": f"mock_msg_{i}",
                    "created_time": datetime.now(timezone.utc).isoformat(),
                    "from": {"id": f"user_{i}"},
                    "to": {"id": "page_demo"},
                    "message": f"This is mock message #{i + 1}",
                }
            )

        logger.info(
            f"[DEMO] Retrieved {len(messages)} messages from {self.platform}",
            extra={"conversation_id": conversation_id or "unknown"},
        )

        return messages

    async def post_content(
        self,
        content: str | None = None,
        media_urls: list[str] | None = None,
        target_id: str | None = None,
    ) -> dict[str, Any]:
        """Mock post content - returns fake post ID."""
        await asyncio.sleep(0.2)

        post_id = f"mock_post_{datetime.now().timestamp()}"
        logger.info(
            f"[DEMO] Posted content to {self.platform}",
            extra={
                "has_content": content is not None,
                "has_media": media_urls is not None,
            },
        )

        return {"post_id": post_id}

    async def get_analytics(self, metric: str, period: str = "day") -> dict[str, Any]:
        """Mock analytics - returns fake data."""
        await asyncio.sleep(0.1)

        # Generate some fake but realistic-looking data
        fake_value = hash(f"{metric}{period}") % 10000

        logger.info(
            f"[DEMO] Retrieved analytics for {metric} ({period}) from {self.platform}",
            extra={"metric": metric, "period": period},
        )

        return {
            "metric": metric,
            "period": period,
            "data": [{"name": metric, "period": period, "values": [{"value": fake_value}]}],
        }
