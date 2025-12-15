"""Custom exceptions and error codes for Meta MCP Server."""


from typing import Any


# Error Code Constants
class ErrorCode:
    """Standard error codes."""

    INVALID_PLATFORM = "INVALID_PLATFORM"
    INVALID_RECIPIENT = "INVALID_RECIPIENT"
    AUTH_FAILED = "AUTH_FAILED"
    API_ERROR = "API_ERROR"
    MISSING_IDENTIFIER = "MISSING_IDENTIFIER"
    PLATFORM_NOT_SUPPORTED = "PLATFORM_NOT_SUPPORTED"
    INVALID_METRIC = "INVALID_METRIC"
    INVALID_PERIOD = "INVALID_PERIOD"
    MISSING_CONTENT = "MISSING_CONTENT"
    MEDIA_UPLOAD_FAILED = "MEDIA_UPLOAD_FAILED"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    NETWORK_ERROR = "NETWORK_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"


# Custom Exceptions


class MetaMCPError(Exception):
    """Base exception for Meta MCP Server."""

    def __init__(self, error_code: str, message: str):
        self.error_code = error_code
        self.message = message
        super().__init__(message)


class PlatformNotSupportedError(MetaMCPError):
    """Raised when operation is not supported on given platform."""

    def __init__(self, platform: str, operation: str):
        super().__init__(
            ErrorCode.PLATFORM_NOT_SUPPORTED,
            f"Operation '{operation}' is not supported on platform '{platform}'",
        )


class AuthenticationError(MetaMCPError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(ErrorCode.AUTH_FAILED, message)


class ValidationError(MetaMCPError):
    """Raised when input validation fails."""

    def __init__(self, message: str):
        super().__init__(ErrorCode.VALIDATION_ERROR, message)


class RateLimitError(MetaMCPError):
    """Raised when rate limit is exceeded."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(ErrorCode.RATE_LIMIT_EXCEEDED, message)


def map_meta_api_error(status_code: int, response_data: dict[str, Any]) -> str:
    """Map Meta API errors to standardized error codes."""
    if status_code == 401 or status_code == 403:
        return ErrorCode.AUTH_FAILED
    elif status_code == 429:
        return ErrorCode.RATE_LIMIT_EXCEEDED
    elif status_code == 400:
        # Parse Meta error response
        error = response_data.get("error", {})
        error_type = error.get("type", "")
        if "OAuthException" in error_type:
            return ErrorCode.AUTH_FAILED
        elif "permission" in error.get("message", "").lower():
            return ErrorCode.INSUFFICIENT_PERMISSIONS
        return ErrorCode.VALIDATION_ERROR
    elif status_code >= 500:
        return ErrorCode.API_ERROR
    return ErrorCode.API_ERROR
