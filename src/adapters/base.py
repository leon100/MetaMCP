"""Base adapter interface for platform implementations."""

from abc import ABC, abstractmethod
from typing import Any


class BasePlatformAdapter(ABC):
    """Abstract base class for platform adapters."""

    def __init__(self, access_token: str, **kwargs: Any) -> None:
        """
        Initialize adapter.

        Args:
            access_token: Platform access token
            **kwargs: Additional platform-specific configuration
        """
        self.access_token = access_token
        self.config = kwargs

    @abstractmethod
    async def send_message(
        self, recipient_id: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """
        Send a message to a recipient.

        Args:
            recipient_id: Recipient identifier
            content: Message content
            media_url: Optional media URL

        Returns:
            Response data containing message_id
        """
        pass

    @abstractmethod
    async def get_messages(
        self, conversation_id: str | None = None, recipient_id: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Retrieve messages from a conversation.

        Args:
            conversation_id: Optional conversation ID
            recipient_id: Optional recipient ID
            limit: Number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        pass

    @abstractmethod
    async def post_content(
        self,
        content: str | None = None,
        media_urls: list[str] | None = None,
        target_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Post content to the platform feed.

        Args:
            content: Text content/caption
            media_urls: Optional media URLs
            target_id: Optional target page/account ID

        Returns:
            Response data containing post_id
        """
        pass

    @abstractmethod
    async def get_analytics(self, metric: str, period: str = "day") -> dict[str, Any]:
        """
        Retrieve analytics/insights.

        Args:
            metric: Metric name
            period: Time period

        Returns:
            Analytics data
        """
        pass
