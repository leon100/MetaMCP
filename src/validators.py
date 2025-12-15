"""Input validation functions."""

import re
from urllib.parse import urlparse

from .errors import ValidationError


def validate_e164_phone(phone: str) -> bool:
    """
    Validate phone number in E.164 format.

    Args:
        phone: Phone number to validate

    Returns:
        True if valid, False otherwise

    Examples:
        +380991234567 (valid)
        +1234567890 (valid)
        380991234567 (invalid - missing +)
    """
    pattern = r"^\+[1-9]\d{1,14}$"
    return bool(re.match(pattern, phone))


def validate_whatsapp_recipient(recipient_id: str) -> None:
    """
    Validate WhatsApp recipient ID (must be E.164 format).

    Args:
        recipient_id: Recipient ID to validate

    Raises:
        ValidationError: If recipient ID is not valid E.164
    """
    if not validate_e164_phone(recipient_id):
        raise ValidationError(
            f"WhatsApp recipient_id must be in E.164 format (e.g., +380991234567), "
            f"got: {recipient_id}"
        )


def validate_url(url: str) -> None:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Raises:
        ValidationError: If URL is not valid
    """
    try:
        result = urlparse(url)
        if not all([result.scheme, result.netloc]):
            raise ValidationError(f"Invalid URL: {url}")
        if result.scheme not in ["http", "https"]:
            raise ValidationError(f"URL must use http or https protocol: {url}")
    except Exception as e:
        raise ValidationError(f"Invalid URL: {url} - {str(e)}")


def validate_media_url(media_url: str | None) -> None:
    """
    Validate media URL if provided.

    Args:
        media_url: Optional media URL

    Raises:
        ValidationError: If URL is provided but invalid
    """
    if media_url:
        validate_url(media_url)


def validate_get_messages_request(conversation_id: str | None, recipient_id: str | None) -> None:
    """
    Validate get_messages request has at least one identifier.

    Args:
        conversation_id: Optional conversation ID
        recipient_id: Optional recipient ID

    Raises:
        ValidationError: If both identifiers are None
    """
    if not conversation_id and not recipient_id:
        raise ValidationError("Either conversation_id or recipient_id must be provided")


def validate_post_content_request(
    platform: str, content: str | None, media_urls: list[str] | None
) -> None:
    """
    Validate post content request.

    Args:
        platform: Platform name
        content: Optional text content
        media_urls: Optional media URLs

    Raises:
        ValidationError: If validation fails
    """
    if not content and not media_urls:
        raise ValidationError("At least one of content or media_urls must be provided")

    if platform == "instagram" and not media_urls:
        raise ValidationError("Instagram posts require media_urls (text-only posts not supported)")

    if media_urls:
        for url in media_urls:
            validate_url(url)
