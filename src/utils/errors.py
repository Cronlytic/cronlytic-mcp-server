"""Custom error classes for the Cronlytic MCP Server."""

from typing import Any, Dict, Optional


class CronlyticError(Exception):
    """Base exception for all Cronlytic MCP Server errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for JSON serialization."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


class ValidationError(CronlyticError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str, value: Any = None) -> None:
        super().__init__(f"Validation error for field '{field}': {message}")
        self.field = field
        self.value = value
        self.details = {"field": field, "value": value}


class AuthenticationError(CronlyticError):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed") -> None:
        super().__init__(message)


class AuthorizationError(CronlyticError):
    """Raised when authorization fails (e.g., job limit exceeded)."""

    def __init__(
        self,
        message: str,
        plan: Optional[str] = None,
        current_count: Optional[int] = None,
        max_allowed: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.details = {
            "plan": plan,
            "current_count": current_count,
            "max_allowed": max_allowed,
        }


class NotFoundError(CronlyticError):
    """Raised when a requested resource is not found."""

    def __init__(self, resource_type: str, resource_id: str) -> None:
        super().__init__(f"{resource_type} with ID '{resource_id}' not found")
        self.resource_type = resource_type
        self.resource_id = resource_id
        self.details = {"resource_type": resource_type, "resource_id": resource_id}


class APIError(CronlyticError):
    """Raised when the Cronlytic API returns an error."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}
        self.details = {
            "status_code": status_code,
            "response_data": self.response_data,
        }


class ConnectionError(CronlyticError):
    """Raised when connection to Cronlytic API fails."""

    def __init__(self, message: str = "Failed to connect to Cronlytic API") -> None:
        super().__init__(message)


class RateLimitError(CronlyticError):
    """Raised when API rate limit is exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message)
        self.retry_after = retry_after
        self.details = {"retry_after": retry_after}


class TimeoutError(CronlyticError):
    """Raised when API request times out."""

    def __init__(self, message: str = "Request timeout") -> None:
        super().__init__(message)