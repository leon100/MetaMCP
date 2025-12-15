"""Pydantic models for Meta MCP Server."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class Platform(str, Enum):
    """Supported platforms."""

    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"


class MetricType(str, Enum):
    """Supported analytics metrics."""

    IMPRESSIONS = "impressions"
    REACH = "reach"
    ENGAGEMENT = "engagement"
    FOLLOWERS = "followers"
    PROFILE_VIEWS = "profile_views"


class Period(str, Enum):
    """Time period for analytics."""

    DAY = "day"
    WEEK = "week"
    MONTH = "month"


# Request Models


class SendMessageRequest(BaseModel):
    """Request model for sending a message."""

    platform: Platform
    recipient_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1, max_length=2000)
    media_url: str | None = None


class GetMessagesRequest(BaseModel):
    """Request model for retrieving messages."""

    platform: Platform
    conversation_id: str | None = None
    recipient_id: str | None = None
    limit: int = Field(default=10, ge=1, le=100)


class PostContentRequest(BaseModel):
    """Request model for posting content."""

    platform: Platform
    content: str | None = Field(None, max_length=2200)
    media_urls: list[str] | None = None
    target_id: str | None = None


class AnalyticsRequest(BaseModel):
    """Request model for analytics."""

    platform: Platform
    metric: MetricType
    period: Period = Period.DAY


# Response Models


class Message(BaseModel):
    """Unified message model."""

    id: str
    platform: Platform
    conversation_id: str
    sender_id: str
    recipient_id: str
    content: str | None = None
    media_url: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_data: dict[str, Any] = Field(default_factory=dict)


class MetaResponse(BaseModel):
    """Standardized response wrapper."""

    success: bool
    platform: Platform
    # Allow dict, list[Message], or list[dict] for raw data
    data: dict[str, Any] | list[Message] | list[dict[str, Any]] | None = None
    message: str | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MetaError(BaseModel):
    """Standardized error response."""

    error_code: str
    error_message: str
    platform: Platform | Literal["unknown"]
    details: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
