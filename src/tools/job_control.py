"""Job control tools for the Cronlytic MCP Server."""

import json
import logging
from typing import Any, Dict, List

from cronlytic_client import CronlyticAPIClient
from utils.auth import AuthConfig
from utils.errors import CronlyticError, ValidationError
from utils.validation import validate_job_id


logger = logging.getLogger(__name__)


# Tool definitions
PAUSE_JOB_TOOL_DEFINITION = {
    "name": "pause_job",
    "description": "Pause execution of a specific cron job",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "minLength": 1,
                "description": "Unique identifier of the job to pause",
            },
        },
        "required": ["job_id"],
        "additionalProperties": False,
    },
}

RESUME_JOB_TOOL_DEFINITION = {
    "name": "resume_job",
    "description": "Resume execution of a paused cron job",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "minLength": 1,
                "description": "Unique identifier of the job to resume",
            },
        },
        "required": ["job_id"],
        "additionalProperties": False,
    },
}

GET_JOB_LOGS_TOOL_DEFINITION = {
    "name": "get_job_logs",
    "description": "Retrieve execution logs for a specific cron job",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "minLength": 1,
                "description": "Unique identifier of the job to get logs for",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 20,
                "description": "Maximum number of log entries to return (default: 20)",
            },
        },
        "required": ["job_id"],
        "additionalProperties": False,
    },
}


async def pause_job_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pause execution of a specific cron job.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job_id

    Returns:
        Dict containing the paused job information

    Raises:
        ValidationError: If job_id validation fails
        CronlyticError: If API call fails
    """
    logger.info("Pausing job execution")
    logger.debug(f"Pause job arguments: {arguments}")

    try:
        # Validate job ID
        job_id = validate_job_id(arguments.get("job_id", ""))

        logger.debug(f"Pausing job with ID: {job_id}")

        # Pause the job via API
        async with CronlyticAPIClient(config) as client:
            job_data = await client.pause_job(job_id)

        logger.info(f"Successfully paused job: {job_data.get('name')} ({job_id})")

        return {
            "success": True,
            "job": job_data,
            "message": f"Job '{job_data.get('name')}' has been paused",
            "status": job_data.get("status"),
        }

    except ValidationError as e:
        logger.warning(f"Validation error in pause_job: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in pause_job: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in pause_job: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


async def resume_job_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Resume execution of a paused cron job.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job_id

    Returns:
        Dict containing the resumed job information

    Raises:
        ValidationError: If job_id validation fails
        CronlyticError: If API call fails
    """
    logger.info("Resuming job execution")
    logger.debug(f"Resume job arguments: {arguments}")

    try:
        # Validate job ID
        job_id = validate_job_id(arguments.get("job_id", ""))

        logger.debug(f"Resuming job with ID: {job_id}")

        # Resume the job via API
        async with CronlyticAPIClient(config) as client:
            job_data = await client.resume_job(job_id)

        logger.info(f"Successfully resumed job: {job_data.get('name')} ({job_id})")

        return {
            "success": True,
            "job": job_data,
            "message": f"Job '{job_data.get('name')}' has been resumed",
            "status": job_data.get("status"),
            "next_run": job_data.get("next_run_at"),
        }

    except ValidationError as e:
        logger.warning(f"Validation error in resume_job: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in resume_job: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in resume_job: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


async def get_job_logs_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Retrieve execution logs for a specific cron job.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job_id and optional limit

    Returns:
        Dict containing the job logs and summary information

    Raises:
        ValidationError: If job_id validation fails
        CronlyticError: If API call fails
    """
    logger.info("Retrieving job logs")
    logger.debug(f"Get job logs arguments: {arguments}")

    try:
        # Validate job ID
        job_id = validate_job_id(arguments.get("job_id", ""))
        limit = arguments.get("limit", 20)

        # Validate limit
        if not isinstance(limit, int) or limit < 1 or limit > 100:
            limit = 20

        logger.debug(f"Getting logs for job ID: {job_id} (limit: {limit})")

        # Fetch logs from API
        async with CronlyticAPIClient(config) as client:
            logs_data = await client.get_job_logs(job_id)

        # Extract logs array and job info
        logs = logs_data.get("logs", [])
        job_info = logs_data.get("job", {})

        # Apply limit to logs
        if len(logs) > limit:
            logs = logs[:limit]
            limited = True
        else:
            limited = False

        # Calculate summary statistics
        total_logs = len(logs)
        status_counts = {}
        recent_executions = 0

        for log in logs:
            status = log.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            # Count recent executions (last 50 logs or all if less)
            recent_executions += 1

        logger.info(f"Successfully retrieved {total_logs} log entries for job {job_id}")

        return {
            "success": True,
            "logs": logs,
            "job": job_info,
            "summary": {
                "total_logs_returned": total_logs,
                "status_breakdown": status_counts,
                "recent_executions": recent_executions,
                "limited": limited,
                "limit_applied": limit if limited else None,
            },
            "message": f"Retrieved {total_logs} log entr{'ies' if total_logs != 1 else 'y'} for job '{job_info.get('name', job_id)}'",
        }

    except ValidationError as e:
        logger.warning(f"Validation error in get_job_logs: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in get_job_logs: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in get_job_logs: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


# Export all tools for easy importing
__all__ = [
    "pause_job_tool",
    "resume_job_tool",
    "get_job_logs_tool",
    "PAUSE_JOB_TOOL_DEFINITION",
    "RESUME_JOB_TOOL_DEFINITION",
    "GET_JOB_LOGS_TOOL_DEFINITION",
]