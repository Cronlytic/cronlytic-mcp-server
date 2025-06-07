"""Authentication and configuration management for Cronlytic MCP Server."""

import json
import logging
import os
from pathlib import Path
from typing import Dict, Optional
from pydantic import BaseModel, Field, validator
from .errors import AuthenticationError


logger = logging.getLogger(__name__)


class AuthConfig(BaseModel):
    """Configuration for Cronlytic API authentication."""

    api_key: str = Field(..., description="Cronlytic API key")
    user_id: str = Field(..., description="Cronlytic User ID")
    base_url: str = Field(
        default="https://api.cronlytic.com/prog",
        description="Base URL for Cronlytic API"
    )
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum number of retries")
    retry_delay: float = Field(default=1.0, description="Base retry delay in seconds")

    @validator("api_key")
    def validate_api_key(cls, v: str) -> str:
        """Validate API key format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("API key cannot be empty")
        return v.strip()

    @validator("user_id")
    def validate_user_id(cls, v: str) -> str:
        """Validate user ID format."""
        if not v or len(v.strip()) == 0:
            raise ValueError("User ID cannot be empty")
        return v.strip()

    @validator("base_url")
    def validate_base_url(cls, v: str) -> str:
        """Validate base URL format."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("Base URL must start with http:// or https://")
        return v.rstrip("/")

    @validator("timeout")
    def validate_timeout(cls, v: int) -> int:
        """Validate timeout value."""
        if v <= 0:
            raise ValueError("Timeout must be positive")
        return v

    @validator("max_retries")
    def validate_max_retries(cls, v: int) -> int:
        """Validate max retries value."""
        if v < 0:
            raise ValueError("Max retries cannot be negative")
        return v

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests."""
        return {
            "X-API-Key": self.api_key,
            "X-User-ID": self.user_id,
            "Content-Type": "application/json",
            "User-Agent": "cronlytic-mcp-server/0.1.0",
        }


def get_config_file_path() -> Path:
    """Get the path to the configuration file."""
    # Check for config file in multiple locations
    possible_paths = [
        Path.cwd() / "cronlytic_config.json",  # Current directory
        Path.home() / ".cronlytic" / "config.json",  # User home directory
        Path("/etc/cronlytic/config.json"),  # System-wide config
    ]

    for path in possible_paths:
        if path.exists():
            return path

    # Return default path for creation
    return Path.home() / ".cronlytic" / "config.json"


def load_config_from_file(config_path: Optional[Path] = None) -> Optional[Dict[str, str]]:
    """Load configuration from JSON file."""
    if config_path is None:
        config_path = get_config_file_path()

    if not config_path.exists():
        logger.debug(f"Config file not found at {config_path}")
        return None

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config_data = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config_data
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load config from {config_path}: {e}")
        return None


def get_auth_config(
    api_key: Optional[str] = None,
    user_id: Optional[str] = None,
    base_url: Optional[str] = None,
    config_file: Optional[str] = None,
) -> AuthConfig:
    """
    Get authentication configuration from multiple sources.

    Priority order:
    1. Direct parameters
    2. Environment variables
    3. Configuration file
    4. Default values (for base_url only)

    Args:
        api_key: Direct API key override
        user_id: Direct user ID override
        base_url: Direct base URL override
        config_file: Path to configuration file

    Returns:
        AuthConfig: Validated configuration object

    Raises:
        AuthenticationError: If required credentials are missing
    """
    config_data = {}

    # Load from config file first
    file_config = load_config_from_file(
        Path(config_file) if config_file else None
    )
    if file_config:
        config_data.update(file_config)

    # Override with environment variables
    env_config = {
        "api_key": os.getenv("CRONLYTIC_API_KEY"),
        "user_id": os.getenv("CRONLYTIC_USER_ID"),
        "base_url": os.getenv("CRONLYTIC_BASE_URL"),
        "timeout": os.getenv("CRONLYTIC_TIMEOUT"),
        "max_retries": os.getenv("CRONLYTIC_MAX_RETRIES"),
        "retry_delay": os.getenv("CRONLYTIC_RETRY_DELAY"),
    }

    # Filter out None values
    env_config = {k: v for k, v in env_config.items() if v is not None}
    config_data.update(env_config)

    # Override with direct parameters
    direct_config = {
        "api_key": api_key,
        "user_id": user_id,
        "base_url": base_url,
    }

    # Filter out None values
    direct_config = {k: v for k, v in direct_config.items() if v is not None}
    config_data.update(direct_config)

    # Check for required fields
    if not config_data.get("api_key"):
        raise AuthenticationError(
            "API key is required. Set CRONLYTIC_API_KEY environment variable, "
            "provide it in config file, or pass it directly."
        )

    if not config_data.get("user_id"):
        raise AuthenticationError(
            "User ID is required. Set CRONLYTIC_USER_ID environment variable, "
            "provide it in config file, or pass it directly."
        )

    try:
        # Convert string values to appropriate types
        if "timeout" in config_data and isinstance(config_data["timeout"], str):
            config_data["timeout"] = int(config_data["timeout"])
        if "max_retries" in config_data and isinstance(config_data["max_retries"], str):
            config_data["max_retries"] = int(config_data["max_retries"])
        if "retry_delay" in config_data and isinstance(config_data["retry_delay"], str):
            config_data["retry_delay"] = float(config_data["retry_delay"])

        return AuthConfig(**config_data)
    except (ValueError, TypeError) as e:
        raise AuthenticationError(f"Invalid configuration: {e}")


def create_example_config(path: Optional[Path] = None) -> Path:
    """Create an example configuration file."""
    if path is None:
        path = Path.home() / ".cronlytic" / "config.json"

    # Ensure directory exists
    path.parent.mkdir(parents=True, exist_ok=True)

    example_config = {
        "api_key": "your_cronlytic_api_key_here",
        "user_id": "your_cronlytic_user_id_here",
        "base_url": "https://api.cronlytic.com/prog",
        "timeout": 30,
        "max_retries": 3,
        "retry_delay": 1.0
    }

    with open(path, "w", encoding="utf-8") as f:
        json.dump(example_config, f, indent=2)

    logger.info(f"Created example configuration file at {path}")
    return path


def validate_auth_config(config: AuthConfig) -> bool:
    """
    Validate that the authentication configuration is working.

    This is a basic validation that checks the configuration format.
    Actual API connectivity should be tested separately.

    Args:
        config: AuthConfig instance to validate

    Returns:
        bool: True if configuration appears valid

    Raises:
        AuthenticationError: If configuration is invalid
    """
    try:
        # Basic validation - the pydantic model should handle most of this
        headers = config.get_headers()

        # Check that headers contain required fields
        required_headers = ["X-API-Key", "X-User-ID", "Content-Type"]
        for header in required_headers:
            if header not in headers:
                raise AuthenticationError(f"Missing required header: {header}")

        logger.info("Authentication configuration validated successfully")
        return True

    except Exception as e:
        raise AuthenticationError(f"Configuration validation failed: {e}")