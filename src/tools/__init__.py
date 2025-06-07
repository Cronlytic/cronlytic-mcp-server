"""Tools package for the Cronlytic MCP Server."""

from .health_check import health_check_tool, HEALTH_CHECK_TOOL_DEFINITION
from .job_management import (
    create_job_tool,
    list_jobs_tool,
    get_job_tool,
    update_job_tool,
    delete_job_tool,
    CREATE_JOB_TOOL_DEFINITION,
    LIST_JOBS_TOOL_DEFINITION,
    GET_JOB_TOOL_DEFINITION,
    UPDATE_JOB_TOOL_DEFINITION,
    DELETE_JOB_TOOL_DEFINITION,
)
from .job_control import (
    pause_job_tool,
    resume_job_tool,
    get_job_logs_tool,
    PAUSE_JOB_TOOL_DEFINITION,
    RESUME_JOB_TOOL_DEFINITION,
    GET_JOB_LOGS_TOOL_DEFINITION,
)

__all__ = [
    # Health check
    "health_check_tool",
    "HEALTH_CHECK_TOOL_DEFINITION",
    # Job management CRUD
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
    # Job control
    "pause_job_tool",
    "resume_job_tool",
    "get_job_logs_tool",
    "PAUSE_JOB_TOOL_DEFINITION",
    "RESUME_JOB_TOOL_DEFINITION",
    "GET_JOB_LOGS_TOOL_DEFINITION",
]