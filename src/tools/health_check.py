"""Health check tool for testing Cronlytic API connectivity."""

import logging
from typing import Any, Dict

from ..cronlytic_client import CronlyticAPIClient
from ..utils.auth import AuthConfig
from ..utils.errors import CronlyticError

logger = logging.getLogger(__name__)


async def health_check_tool(config: AuthConfig) -> Dict[str, Any]:
    """
    Perform a comprehensive health check of the Cronlytic API connection.

    This tool tests:
    - API connectivity
    - Authentication validity
    - Response times
    - Basic functionality

    Args:
        config: Authentication configuration

    Returns:
        Dict containing health check results with status, timing, and diagnostic info
    """
    logger.info("Starting Cronlytic API health check")

    result = {
        "tool": "health_check",
        "timestamp": None,
        "status": "unknown",
        "connectivity": False,
        "authentication": False,
        "response_time_ms": None,
        "api_version": None,
        "base_url": config.base_url,
        "details": {},
        "errors": [],
        "recommendations": []
    }

    try:
        async with CronlyticAPIClient(config) as client:
            # Test basic connectivity and authentication
            health_data = await client.health_check()

            result.update({
                "status": health_data.get("status", "unknown"),
                "connectivity": health_data.get("connected", False),
                "authentication": health_data.get("status") == "healthy",
                "response_time_ms": health_data.get("response_time_ms"),
                "details": {
                    "api_response": health_data.get("api_response", {}),
                    "base_url": health_data.get("base_url"),
                    "user_agent": config.get_headers().get("User-Agent", "unknown"),
                }
            })

            # If basic health check passed, try to list jobs to test authentication
            if health_data.get("status") == "healthy":
                try:
                    jobs = await client.list_jobs()
                    result["details"]["job_count"] = len(jobs) if isinstance(jobs, list) else 0
                    result["details"]["can_list_jobs"] = True

                    # Additional recommendations based on job count
                    job_count = result["details"]["job_count"]
                    if job_count == 0:
                        result["recommendations"].append(
                            "No jobs found. You can create your first job using the create_job tool."
                        )
                    else:
                        result["recommendations"].append(
                            f"Found {job_count} job(s). All systems appear to be working correctly."
                        )

                except Exception as e:
                    result["details"]["can_list_jobs"] = False
                    result["errors"].append(f"Failed to list jobs: {str(e)}")
                    result["recommendations"].append(
                        "Authentication succeeded but job listing failed. Check API permissions."
                    )

            # Performance assessment
            response_time = result.get("response_time_ms", 0)
            if response_time:
                if response_time < 200:
                    result["details"]["performance"] = "excellent"
                elif response_time < 500:
                    result["details"]["performance"] = "good"
                elif response_time < 1000:
                    result["details"]["performance"] = "fair"
                    result["recommendations"].append(
                        "Response time is a bit slow. Check your network connection."
                    )
                else:
                    result["details"]["performance"] = "poor"
                    result["recommendations"].append(
                        "Response time is very slow. Check your network connection and API status."
                    )

    except CronlyticError as e:
        result["status"] = "error"
        result["connectivity"] = False
        result["authentication"] = False
        result["errors"].append(f"Cronlytic API error: {e.message}")
        result["details"]["error_type"] = type(e).__name__
        result["details"]["error_details"] = e.details

        # Specific recommendations based on error type
        if "AuthenticationError" in str(type(e)):
            result["recommendations"].extend([
                "Check that your API key and User ID are correct",
                "Verify that your credentials are not expired",
                "Ensure you're using the correct environment variables or config file"
            ])
        elif "ConnectionError" in str(type(e)):
            result["recommendations"].extend([
                "Check your internet connection",
                "Verify that api.cronlytic.com is accessible",
                "Check if there are any firewall restrictions"
            ])
        else:
            result["recommendations"].append(
                f"Encountered {type(e).__name__}: {e.message}"
            )

    except Exception as e:
        result["status"] = "error"
        result["connectivity"] = False
        result["authentication"] = False
        result["errors"].append(f"Unexpected error: {str(e)}")
        result["details"]["error_type"] = type(e).__name__
        result["recommendations"].append(
            "An unexpected error occurred. Please check your configuration and try again."
        )

    # Add timestamp
    from datetime import datetime
    result["timestamp"] = datetime.utcnow().isoformat() + "Z"

    # Summary message
    if result["status"] == "healthy":
        result["summary"] = "✅ Cronlytic API connection is healthy and working correctly"
    elif result["status"] == "unhealthy":
        result["summary"] = "⚠️ Cronlytic API connection has issues but is partially working"
    else:
        result["summary"] = "❌ Cronlytic API connection failed"

    logger.info(f"Health check completed: {result['summary']}")

    return result


# Tool definition for MCP
HEALTH_CHECK_TOOL_DEFINITION = {
    "name": "health_check",
    "description": "Test connectivity and authentication with the Cronlytic API",
    "inputSchema": {
        "type": "object",
        "properties": {},
        "required": []
    }
}