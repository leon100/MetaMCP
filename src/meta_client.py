"""Meta API client with connection pooling and retry logic."""

from typing import Any

from tenacity import retry, stop_after_attempt, wait_exponential

from .adapters import (
    BasePlatformAdapter,
    FacebookAdapter,
    InstagramAdapter,
    MockPlatformAdapter,
    WhatsAppAdapter,
)
from .config import Settings
from .errors import AuthenticationError, ErrorCode, MetaMCPError
from .logging_config import logger


class MetaClient:
    """Meta API client with platform adapter factory."""

    def __init__(self, settings: Settings) -> None:
        """
        Initialize Meta client.

        Args:
            settings: Application settings
        """
        self.settings = settings
        self.api_version = settings.meta_api_version

    def get_adapter(self, platform: str) -> BasePlatformAdapter:
        """
        Get platform-specific adapter.

        Args:
            platform: Platform name (facebook, instagram, whatsapp)

        Returns:
            Platform adapter instance

        Raises:
            AuthenticationError: If platform is not configured
        """
        if self.settings.demo_mode:
            logger.info(f"Using MockPlatformAdapter for {platform} (demo mode)")
            return MockPlatformAdapter(access_token="demo", platform=platform)

        # Validate platform is configured
        if not self.settings.validate_platform_config(platform):
            raise AuthenticationError(
                f"Platform '{platform}' is not configured. "
                f"Please provide the required access token in .env file."
            )

        token = self.settings.get_platform_token(platform)
        if not token:
            raise AuthenticationError(f"No access token configured for platform: {platform}")

        # Create platform-specific adapter
        if platform == "facebook":
            return FacebookAdapter(access_token=token, api_version=self.api_version)
        elif platform == "instagram":
            return InstagramAdapter(access_token=token, api_version=self.api_version)
        elif platform == "whatsapp":
            phone_number_id = self.settings.whatsapp_phone_number_id
            return WhatsAppAdapter(
                access_token=token,
                phone_number_id=phone_number_id,
                api_version=self.api_version,
            )
        else:
            raise MetaMCPError(ErrorCode.INVALID_PLATFORM, f"Unknown platform: {platform}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def send_message_with_retry(
        self, platform: str, recipient_id: str, content: str, media_url: str | None = None
    ) -> dict[str, Any]:
        """
        Send message with retry logic.

        Args:
            platform: Platform name
            recipient_id: Recipient ID
            content: Message content
            media_url: Optional media URL

        Returns:
            Response data
        """
        adapter = self.get_adapter(platform)
        return await adapter.send_message(recipient_id, content, media_url)
