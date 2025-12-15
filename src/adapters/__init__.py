"""Platform adapters package."""

from .base import BasePlatformAdapter
from .facebook import FacebookAdapter
from .instagram import InstagramAdapter
from .mock import MockPlatformAdapter
from .whatsapp import WhatsAppAdapter

__all__ = [
    "BasePlatformAdapter",
    "FacebookAdapter",
    "InstagramAdapter",
    "WhatsAppAdapter",
    "MockPlatformAdapter",
]
