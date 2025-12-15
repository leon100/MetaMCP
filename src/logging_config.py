"""Centralized logging configuration."""

import logging
import sys
from typing import Any

from pythonjsonlogger import json as jsonlogger

from .config import settings


class SanitizingFormatter(jsonlogger.JsonFormatter):
    """JSON formatter that sanitizes sensitive information."""

    SENSITIVE_KEYS = {"access_token", "token", "secret", "password", "api_key"}

    def process_log_record(self, log_record: dict[str, Any]) -> dict[str, Any]:
        """Sanitize sensitive fields in log record."""
        for key in list(log_record.keys()):
            if any(sensitive in key.lower() for sensitive in self.SENSITIVE_KEYS):
                log_record[key] = "***REDACTED***"
        return log_record


def setup_logging() -> logging.Logger:
    """
    Configure logging for the application.

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("meta_mcp")
    logger.setLevel(getattr(logging, settings.log_level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler with JSON formatting
    # Use stderr to avoid interfering with MCP JSON-RPC communication over stdout
    handler = logging.StreamHandler(sys.stderr)
    formatter = SanitizingFormatter(
        "%(timestamp)s %(level)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logging()
