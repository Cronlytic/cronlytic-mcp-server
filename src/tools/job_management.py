"""Job management tools for the Cronlytic MCP Server."""

import json
import logging
from typing import Any, Dict, List

from cronlytic_client import CronlyticAPIClient
from utils.auth import AuthConfig
from utils.errors import CronlyticError, ValidationError
from utils.validation import validate_complete_job_data, validate_job_id


logger = logging.getLogger(__name__)


# Tool definitions
CREATE_JOB_TOOL_DEFINITION = {
    "name": "create_job",
    "description": "Create a new cron job in Cronlytic with comprehensive validation",
    "inputSchema": {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9_-]+$",
                "minLength": 1,
                "maxLength": 50,
                "description": "Job name (alphanumeric, hyphens, underscores only)",
            },
            "url": {
                "type": "string",
                "format": "uri",
                "description": "Webhook URL to call (must be http:// or https://)",
            },
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                "default": "GET",
                "description": "HTTP method for the webhook call",
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers to include with the request (can be empty {})",
                "additionalProperties": {
                    "type": "string"
                },
                "default": {},
            },
            "body": {
                "type": "string",
                "description": "Request body content (can be empty string)",
                "default": "",
            },
            "cron_expression": {
                "type": "string",
                "pattern": "^[0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+$",
                "description": "5-field cron expression (minute hour day month day-of-week)",
            },
        },
        "required": ["name", "url", "method", "headers", "body", "cron_expression"],
    },
}

LIST_JOBS_TOOL_DEFINITION = {
    "name": "list_jobs",
    "description": "List all cron jobs for the authenticated user with status information",
    "inputSchema": {
        "type": "object",
        "properties": {
            "include_paused": {
                "type": "boolean",
                "default": True,
                "description": "Whether to include paused jobs in the results",
            },
            "limit": {
                "type": "integer",
                "minimum": 1,
                "maximum": 100,
                "default": 50,
                "description": "Maximum number of jobs to return",
            },
        },
        "additionalProperties": False,
    },
}

GET_JOB_TOOL_DEFINITION = {
    "name": "get_job",
    "description": "Get detailed information about a specific cron job by ID",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "minLength": 1,
                "description": "Unique identifier of the job to retrieve",
            },
        },
        "required": ["job_id"],
        "additionalProperties": False,
    },
}


async def create_job_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new cron job in Cronlytic.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job data

    Returns:
        Dict containing the created job information

    Raises:
        ValidationError: If input validation fails
        CronlyticError: If API call fails
    """
    logger.info("Creating new cron job")
    logger.debug(f"Job data: {arguments}")

    try:
        # Validate the job data
        validated_data = validate_complete_job_data(arguments)

        logger.debug(f"Validated job data: {validated_data}")

        # Create the job via API
        async with CronlyticAPIClient(config) as client:
            job_data = await client.create_job(validated_data)

        logger.info(f"Successfully created job with ID: {job_data.get('id')}")

        return {
            "success": True,
            "job": job_data,
            "message": f"Job '{job_data.get('name')}' created successfully",
            "next_run": job_data.get("next_run_at"),
        }

    except ValidationError as e:
        logger.warning(f"Validation error in create_job: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in create_job: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in create_job: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


async def list_jobs_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    List all cron jobs for the authenticated user.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing filtering options

    Returns:
        Dict containing the list of jobs and summary information

    Raises:
        CronlyticError: If API call fails
    """
    logger.info("Listing cron jobs")
    logger.debug(f"List arguments: {arguments}")

    try:
        # Get optional parameters
        include_paused = arguments.get("include_paused", True)
        limit = arguments.get("limit", 50)

        # Fetch jobs from API
        async with CronlyticAPIClient(config) as client:
            jobs_data = await client.list_jobs()

        # Filter jobs if needed
        if not include_paused:
            jobs_data = [job for job in jobs_data if job.get("status") != "paused"]

        # Apply limit
        if limit and len(jobs_data) > limit:
            jobs_data = jobs_data[:limit]
            limited = True
        else:
            limited = False

        # Calculate summary statistics
        total_count = len(jobs_data)
        status_counts = {}
        for job in jobs_data:
            status = job.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        logger.info(f"Successfully retrieved {total_count} jobs")

        return {
            "success": True,
            "jobs": jobs_data,
            "summary": {
                "total_count": total_count,
                "status_breakdown": status_counts,
                "limited": limited,
                "limit_applied": limit if limited else None,
            },
            "message": f"Found {total_count} job{'s' if total_count != 1 else ''}",
        }

    except CronlyticError as e:
        logger.error(f"API error in list_jobs: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in list_jobs: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


async def get_job_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get detailed information about a specific cron job.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job_id

    Returns:
        Dict containing the job information

    Raises:
        ValidationError: If job_id validation fails
        CronlyticError: If API call fails
    """
    logger.info("Getting job details")
    logger.debug(f"Get job arguments: {arguments}")

    try:
        # Validate job ID
        job_id = validate_job_id(arguments.get("job_id", ""))

        logger.debug(f"Getting job with ID: {job_id}")

        # Fetch job from API
        async with CronlyticAPIClient(config) as client:
            job_data = await client.get_job(job_id)

        logger.info(f"Successfully retrieved job: {job_data.get('name')} ({job_id})")

        return {
            "success": True,
            "job": job_data,
            "message": f"Retrieved job '{job_data.get('name')}'",
        }

    except ValidationError as e:
        logger.warning(f"Validation error in get_job: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in get_job: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in get_job: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


UPDATE_JOB_TOOL_DEFINITION = {
    "name": "update_job",
    "description": "Update an existing cron job with new configuration",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "minLength": 1,
                "description": "Unique identifier of the job to update",
            },
            "name": {
                "type": "string",
                "pattern": "^[a-zA-Z0-9_-]+$",
                "minLength": 1,
                "maxLength": 50,
                "description": "Job name (alphanumeric, hyphens, underscores only)",
            },
            "url": {
                "type": "string",
                "format": "uri",
                "description": "Webhook URL to call (must be http:// or https://)",
            },
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                "default": "GET",
                "description": "HTTP method for the webhook call",
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers to include with the request (optional)",
                "additionalProperties": {
                    "type": "string"
                },
            },
            "body": {
                "type": "string",
                "description": "Request body content (optional, for POST/PUT requests)",
                "default": "",
            },
            "cron_expression": {
                "type": "string",
                "pattern": "^[0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+ [0-9*,/-]+$",
                "description": "5-field cron expression (minute hour day month day-of-week)",
            },
        },
        "required": ["job_id", "name", "url", "cron_expression"],
    },
}

DELETE_JOB_TOOL_DEFINITION = {
    "name": "delete_job",
    "description": "Permanently delete a cron job (this action cannot be undone)",
    "inputSchema": {
        "type": "object",
        "properties": {
            "job_id": {
                "type": "string",
                "minLength": 1,
                "description": "Unique identifier of the job to delete",
            },
            "confirm": {
                "type": "boolean",
                "default": False,
                "description": "Confirmation that you want to permanently delete this job",
            },
        },
        "required": ["job_id"],
        "additionalProperties": False,
    },
}


async def update_job_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update an existing cron job configuration.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job_id and complete job data

    Returns:
        Dict containing the updated job information

    Raises:
        ValidationError: If input validation fails
        CronlyticError: If API call fails
    """
    logger.info("Updating job configuration")
    logger.debug(f"Update job arguments: {arguments}")

    try:
        # Validate job ID
        job_id = validate_job_id(arguments.get("job_id", ""))

        # Extract job data (exclude job_id for the API call)
        job_data = {k: v for k, v in arguments.items() if k != "job_id"}

        # Validate the job data
        validated_data = validate_complete_job_data(job_data)

        logger.debug(f"Validated job data for update: {validated_data}")

        # Update the job via API
        async with CronlyticAPIClient(config) as client:
            updated_job = await client.update_job(job_id, validated_data)

        logger.info(f"Successfully updated job with ID: {job_id}")

        return {
            "success": True,
            "job": updated_job,
            "message": f"Job '{updated_job.get('name')}' updated successfully",
            "changes_applied": True,
            "next_run": updated_job.get("next_run_at"),
        }

    except ValidationError as e:
        logger.warning(f"Validation error in update_job: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in update_job: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in update_job: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


async def delete_job_tool(config: AuthConfig, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Permanently delete a cron job.

    Args:
        config: Authentication configuration
        arguments: Tool arguments containing job_id and optional confirmation

    Returns:
        Dict containing the deletion confirmation

    Raises:
        ValidationError: If job_id validation fails
        CronlyticError: If API call fails
    """
    logger.info("Deleting job")
    logger.debug(f"Delete job arguments: {arguments}")

    try:
        # Validate job ID
        job_id = validate_job_id(arguments.get("job_id", ""))
        confirm = arguments.get("confirm", False)

        logger.debug(f"Deleting job with ID: {job_id} (confirmed: {confirm})")

        # Check for confirmation (optional safety feature)
        if not confirm:
            logger.warning(f"Job deletion attempted without confirmation for job {job_id}")
            return {
                "success": False,
                "error": "Confirmation Required",
                "message": "Job deletion requires confirmation. Set 'confirm' parameter to true to proceed.",
                "warning": "This action cannot be undone. The job and all its execution history will be permanently deleted.",
                "job_id": job_id,
            }

        # First get job info for the response
        async with CronlyticAPIClient(config) as client:
            try:
                job_info = await client.get_job(job_id)
                job_name = job_info.get("name", job_id)
            except Exception:
                job_name = job_id  # Fallback if we can't get job info

            # Delete the job via API
            deletion_result = await client.delete_job(job_id)

        logger.info(f"Successfully deleted job: {job_name} ({job_id})")

        return {
            "success": True,
            "message": f"Job '{job_name}' has been permanently deleted",
            "job_id": job_id,
            "deleted": True,
            "deletion_timestamp": deletion_result.get("deleted_at"),
        }

    except ValidationError as e:
        logger.warning(f"Validation error in delete_job: {e}")
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(e),
            "field": e.field,
            "value": e.value,
        }

    except CronlyticError as e:
        logger.error(f"API error in delete_job: {e}")
        return {
            "success": False,
            "error": e.__class__.__name__,
            "message": e.message,
            "details": e.details,
        }

    except Exception as e:
        logger.error(f"Unexpected error in delete_job: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Unexpected Error",
            "message": str(e),
        }


# Export all tools for easy importing
__all__ = [
    "create_job_tool",
    "list_jobs_tool",
    "get_job_tool",
    "update_job_tool",
    "delete_job_tool",
    "CREATE_JOB_TOOL_DEFINITION",
    "LIST_JOBS_TOOL_DEFINITION",
    "GET_JOB_TOOL_DEFINITION",
    "UPDATE_JOB_TOOL_DEFINITION",
    "DELETE_JOB_TOOL_DEFINITION",
]