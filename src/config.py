"""Configuration management using pydantic-settings."""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Determine env file path: prioritize local absolute path if it exists, else default
_local_env = "/home/leon/projects/MetaMCP/.env"
_env_file = _local_env if os.path.exists(_local_env) else ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=_env_file,
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Required Meta App Credentials
    meta_app_id: str = ""
    meta_app_secret: str = ""

    # Platform-specific tokens (optional, at least one should be provided in production)
    facebook_page_access_token: str = ""
    instagram_access_token: str = ""
    whatsapp_access_token: str = ""
    whatsapp_phone_number_id: str = ""

    # Optional configuration
    meta_api_version: str = "v21.0"
    log_level: str = "INFO"

    # Demo mode flag
    demo_mode: bool = False

    def get_platform_token(self, platform: str) -> str | None:
        """
        Get access token for specific platform.

        Args:
            platform: Platform name (facebook, instagram, whatsapp)

        Returns:
            Access token or None if not configured
        """
        token_map = {
            "facebook": self.facebook_page_access_token,
            "instagram": self.instagram_access_token,
            "whatsapp": self.whatsapp_access_token,
        }
        return token_map.get(platform) or None

    def validate_platform_config(self, platform: str) -> bool:
        """
        Check if platform is properly configured.

        Args:
            platform: Platform name

        Returns:
            True if configured, False otherwise
        """
        if self.demo_mode:
            return True

        token = self.get_platform_token(platform)
        if not token:
            return False

        if platform == "whatsapp" and not self.whatsapp_phone_number_id:
            return False

        return True


# Global settings instance
settings = Settings()
