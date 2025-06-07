"""Input validation utilities for the Cronlytic MCP Server."""

import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from croniter import croniter
from .errors import ValidationError


# Validation patterns
JOB_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
CRON_FIELD_PATTERN = re.compile(r"^[0-9*,/-]+$")


def validate_job_name(name: str) -> str:
    """
    Validate job name according to Cronlytic API requirements.

    Rules:
    - Only letters, numbers, hyphens (-), and underscores (_) allowed
    - Length: 1-50 characters

    Args:
        name: Job name to validate

    Returns:
        str: Validated job name

    Raises:
        ValidationError: If validation fails
    """
    if not name:
        raise ValidationError("name", "Job name cannot be empty", name)

    name = name.strip()

    if len(name) == 0:
        raise ValidationError("name", "Job name cannot be empty", name)

    if len(name) > 50:
        raise ValidationError(
            "name", "Job name cannot exceed 50 characters", name
        )

    if not JOB_NAME_PATTERN.match(name):
        raise ValidationError(
            "name",
            "Job name can only contain letters, numbers, hyphens (-), and underscores (_)",
            name,
        )

    return name


def validate_url(url: str) -> str:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Returns:
        str: Validated URL

    Raises:
        ValidationError: If validation fails
    """
    if not url:
        raise ValidationError("url", "URL cannot be empty", url)

    url = url.strip()

    if not url:
        raise ValidationError("url", "URL cannot be empty", url)

    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            raise ValidationError("url", "URL must include a scheme (http:// or https://)", url)

        if parsed.scheme not in ("http", "https"):
            raise ValidationError(
                "url", "URL scheme must be http:// or https://", url
            )

        if not parsed.netloc:
            raise ValidationError("url", "URL must include a domain name", url)

        # Basic security check - no local/private URLs in production
        # This is a basic check and can be expanded
        if parsed.hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
            # Allow localhost in development
            pass  # Could add environment check here

        return url

    except ValueError as e:
        raise ValidationError("url", f"Invalid URL format: {e}", url)


def validate_http_method(method: str) -> str:
    """
    Validate HTTP method.

    Args:
        method: HTTP method to validate

    Returns:
        str: Validated HTTP method (uppercase)

    Raises:
        ValidationError: If validation fails
    """
    if not method:
        raise ValidationError("method", "HTTP method cannot be empty", method)

    method = method.strip().upper()

    allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}

    if method not in allowed_methods:
        raise ValidationError(
            "method",
            f"HTTP method must be one of: {', '.join(sorted(allowed_methods))}",
            method,
        )

    return method


def validate_cron_expression(expression: str) -> str:
    """
    Validate cron expression format and syntax.

    Supports standard 5-field cron format: minute hour day month day-of-week

    Args:
        expression: Cron expression to validate

    Returns:
        str: Validated cron expression

    Raises:
        ValidationError: If validation fails
    """
    if not expression:
        raise ValidationError("cron_expression", "Cron expression cannot be empty", expression)

    expression = expression.strip()

    if not expression:
        raise ValidationError("cron_expression", "Cron expression cannot be empty", expression)

    # Split into fields
    fields = expression.split()

    if len(fields) != 5:
        raise ValidationError(
            "cron_expression",
            "Cron expression must have exactly 5 fields (minute hour day month day-of-week)",
            expression,
        )

    # Basic pattern validation for each field
    for i, field in enumerate(fields):
        if not CRON_FIELD_PATTERN.match(field):
            field_names = ["minute", "hour", "day", "month", "day-of-week"]
            raise ValidationError(
                "cron_expression",
                f"Invalid {field_names[i]} field: '{field}'. Only numbers, *, -, /, and , are allowed",
                expression,
            )

    # Use croniter for more detailed validation
    try:
        # Try to create a croniter object to validate the expression
        cron = croniter(expression)
        # Try to get the next run time to ensure it's valid
        next_run = cron.get_next()
        if next_run is None:
            raise ValueError("Cannot compute next execution time")

    except (ValueError, TypeError) as e:
        raise ValidationError(
            "cron_expression",
            f"Invalid cron expression: {e}",
            expression,
        )

    return expression


def validate_headers(headers: dict) -> dict:
    """
    Validate HTTP headers.

    Args:
        headers: Dictionary of headers to validate

    Returns:
        dict: Validated headers

    Raises:
        ValidationError: If validation fails
    """
    if headers is None:
        return {}

    if not isinstance(headers, dict):
        raise ValidationError(
            "headers", "Headers must be a dictionary", headers
        )

    validated_headers = {}

    for key, value in headers.items():
        if not isinstance(key, str):
            raise ValidationError(
                "headers", f"Header key must be a string, got {type(key)}", key
            )

        if not isinstance(value, str):
            raise ValidationError(
                "headers", f"Header value must be a string, got {type(value)} for key '{key}'", value
            )

        # Basic header validation
        key = key.strip()
        value = value.strip()

        if not key:
            raise ValidationError("headers", "Header key cannot be empty", key)

        # Store validated headers
        validated_headers[key] = value

    return validated_headers


def validate_request_body(body: str) -> str:
    """
    Validate request body.

    Args:
        body: Request body to validate

    Returns:
        str: Validated request body

    Raises:
        ValidationError: If validation fails
    """
    if body is None:
        return ""

    if not isinstance(body, str):
        raise ValidationError(
            "body", f"Request body must be a string, got {type(body)}", body
        )

    # No specific validation for body content - it can be any string
    return body


def get_cron_description(expression: str) -> str:
    """
    Get a human-readable description of a cron expression.

    Args:
        expression: Valid cron expression

    Returns:
        str: Human-readable description
    """
    try:
        # Use croniter to parse and get some information
        cron = croniter(expression)
        next_run = cron.get_next()

        # Basic descriptions for common patterns
        common_patterns = {
            "* * * * *": "Every minute",
            "*/5 * * * *": "Every 5 minutes",
            "*/10 * * * *": "Every 10 minutes",
            "*/15 * * * *": "Every 15 minutes",
            "*/30 * * * *": "Every 30 minutes",
            "0 * * * *": "Every hour",
            "0 */2 * * *": "Every 2 hours",
            "0 */6 * * *": "Every 6 hours",
            "0 */12 * * *": "Every 12 hours",
            "0 0 * * *": "Daily at midnight",
            "0 9 * * *": "Daily at 9:00 AM",
            "0 0 * * 0": "Weekly on Sunday at midnight",
            "0 0 1 * *": "Monthly on the 1st at midnight",
            "0 0 1 1 *": "Yearly on January 1st at midnight",
        }

        if expression in common_patterns:
            return common_patterns[expression]

        # For other expressions, provide a generic description
        return f"Custom schedule (next run calculated dynamically)"

    except Exception:
        return "Custom cron schedule"


def validate_complete_job_data(data: dict) -> dict:
    """
    Validate complete job data for creation or update.

    Args:
        data: Dictionary containing job data

    Returns:
        dict: Validated job data

    Raises:
        ValidationError: If any validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError("job_data", "Job data must be a dictionary", data)

    # Required fields
    required_fields = ["name", "url", "method", "headers", "body", "cron_expression"]

    for field in required_fields:
        if field not in data:
            raise ValidationError(field, f"Required field '{field}' is missing", None)

    # Validate each field
    validated_data = {}

    validated_data["name"] = validate_job_name(data["name"])
    validated_data["url"] = validate_url(data["url"])
    validated_data["method"] = validate_http_method(data["method"])
    validated_data["headers"] = validate_headers(data["headers"])
    validated_data["body"] = validate_request_body(data["body"])
    validated_data["cron_expression"] = validate_cron_expression(data["cron_expression"])

    return validated_data


def get_next_execution_times(expression: str, count: int = 5) -> List[str]:
    """
    Get the next N execution times for a cron expression.

    Args:
        expression: Valid cron expression
        count: Number of next execution times to return

    Returns:
        List[str]: List of ISO formatted datetime strings
    """
    try:
        cron = croniter(expression)
        times = []

        for _ in range(count):
            next_time = cron.get_next()
            times.append(next_time.isoformat() + "Z")

        return times

    except Exception:
        return []


def validate_job_id(job_id: str) -> str:
    """
    Validate job ID format.

    Args:
        job_id: Job ID to validate

    Returns:
        str: Validated job ID

    Raises:
        ValidationError: If validation fails
    """
    if not job_id:
        raise ValidationError("job_id", "Job ID cannot be empty", job_id)

    job_id = job_id.strip()

    if not job_id:
        raise ValidationError("job_id", "Job ID cannot be empty", job_id)

    # Basic ID format validation (flexible)
    if len(job_id) < 3:
        raise ValidationError("job_id", "Job ID appears to be too short", job_id)

    return job_id