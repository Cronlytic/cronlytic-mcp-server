"""Main MCP server implementation for Cronlytic API integration."""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional, Sequence

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    EmbeddedResource,
    GetPromptRequest,
    GetPromptResult,
    ListPromptsRequest,
    ListPromptsResult,
    ListResourcesRequest,
    ListResourcesResult,
    ListToolsRequest,
    ListToolsResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    ReadResourceRequest,
    ReadResourceResult,
    Resource,
    Tool,
    TextContent,
)
from cronlytic_client import CronlyticAPIClient
from tools.health_check import health_check_tool, HEALTH_CHECK_TOOL_DEFINITION
from tools.job_management import (
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
from tools.job_control import (
    pause_job_tool,
    resume_job_tool,
    get_job_logs_tool,
    PAUSE_JOB_TOOL_DEFINITION,
    RESUME_JOB_TOOL_DEFINITION,
    GET_JOB_LOGS_TOOL_DEFINITION,
)
from utils.auth import AuthConfig, get_auth_config
from utils.errors import CronlyticError
from utils.performance import performance_tracked, get_performance_report

# Import resource providers
from resources import JobResourceProvider, CronTemplatesProvider

# Import prompts
from prompts import get_all_prompts


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)


class CronlyticMCPServer:
    """
    Cronlytic MCP Server implementation.

    Provides MCP tools, resources, and prompts for managing cron jobs
    through the Cronlytic API.
    """

    def __init__(self, config: Optional[AuthConfig] = None) -> None:
        """
        Initialize the Cronlytic MCP Server.

        Args:
            config: Optional authentication configuration. If not provided,
                   will be loaded from environment variables or config files.
        """
        self.config = config
        self.server = Server("cronlytic-mcp-server")
        self.client: Optional[CronlyticAPIClient] = None

        # Initialize resource providers
        self.job_resource_provider: Optional[JobResourceProvider] = None
        self.cron_templates_provider = CronTemplatesProvider()

        # Setup server handlers
        self._setup_handlers()

        logger.info("Cronlytic MCP Server initialized")

    def _setup_handlers(self) -> None:
        """Setup MCP server handlers."""

        @self.server.list_tools()
        async def handle_list_tools() -> List[Tool]:
            """Handle list tools request."""
            logger.debug("Handling list_tools request")

            tools = [
                # Health check tool
                Tool(
                    name=HEALTH_CHECK_TOOL_DEFINITION["name"],
                    description=HEALTH_CHECK_TOOL_DEFINITION["description"],
                    inputSchema=HEALTH_CHECK_TOOL_DEFINITION["inputSchema"],
                ),
                # Job management CRUD tools
                Tool(
                    name=CREATE_JOB_TOOL_DEFINITION["name"],
                    description=CREATE_JOB_TOOL_DEFINITION["description"],
                    inputSchema=CREATE_JOB_TOOL_DEFINITION["inputSchema"],
                ),
                Tool(
                    name=LIST_JOBS_TOOL_DEFINITION["name"],
                    description=LIST_JOBS_TOOL_DEFINITION["description"],
                    inputSchema=LIST_JOBS_TOOL_DEFINITION["inputSchema"],
                ),
                Tool(
                    name=GET_JOB_TOOL_DEFINITION["name"],
                    description=GET_JOB_TOOL_DEFINITION["description"],
                    inputSchema=GET_JOB_TOOL_DEFINITION["inputSchema"],
                ),
                Tool(
                    name=UPDATE_JOB_TOOL_DEFINITION["name"],
                    description=UPDATE_JOB_TOOL_DEFINITION["description"],
                    inputSchema=UPDATE_JOB_TOOL_DEFINITION["inputSchema"],
                ),
                Tool(
                    name=DELETE_JOB_TOOL_DEFINITION["name"],
                    description=DELETE_JOB_TOOL_DEFINITION["description"],
                    inputSchema=DELETE_JOB_TOOL_DEFINITION["inputSchema"],
                ),
                # Job control tools
                Tool(
                    name=PAUSE_JOB_TOOL_DEFINITION["name"],
                    description=PAUSE_JOB_TOOL_DEFINITION["description"],
                    inputSchema=PAUSE_JOB_TOOL_DEFINITION["inputSchema"],
                ),
                Tool(
                    name=RESUME_JOB_TOOL_DEFINITION["name"],
                    description=RESUME_JOB_TOOL_DEFINITION["description"],
                    inputSchema=RESUME_JOB_TOOL_DEFINITION["inputSchema"],
                ),
                Tool(
                    name=GET_JOB_LOGS_TOOL_DEFINITION["name"],
                    description=GET_JOB_LOGS_TOOL_DEFINITION["description"],
                    inputSchema=GET_JOB_LOGS_TOOL_DEFINITION["inputSchema"],
                ),
            ]

            logger.debug(f"Returning {len(tools)} tools")
            return tools

        @self.server.call_tool()
        @performance_tracked("tool_call")
        async def handle_call_tool(
            name: str, arguments: Dict[str, Any]
        ) -> List[TextContent]:
            """Handle tool call request."""
            logger.info(f"Handling tool call: {name}")
            logger.debug(f"Tool arguments: {arguments}")

            try:
                # Ensure we have configuration
                if self.config is None:
                    self.config = get_auth_config()

                # Handle different tools
                if name == "health_check":
                    result = await health_check_tool(self.config)
                    output = self._format_health_check_result(result)
                    return [TextContent(type="text", text=output)]

                elif name == "create_job":
                    result = await create_job_tool(self.config, arguments)
                    output = self._format_job_result(result, "Job Creation")
                    return [TextContent(type="text", text=output)]

                elif name == "list_jobs":
                    result = await list_jobs_tool(self.config, arguments)
                    output = self._format_job_list_result(result)
                    return [TextContent(type="text", text=output)]

                elif name == "get_job":
                    result = await get_job_tool(self.config, arguments)
                    output = self._format_job_result(result, "Job Details")
                    return [TextContent(type="text", text=output)]

                elif name == "update_job":
                    result = await update_job_tool(self.config, arguments)
                    output = self._format_job_result(result, "Job Update")
                    return [TextContent(type="text", text=output)]

                elif name == "delete_job":
                    result = await delete_job_tool(self.config, arguments)
                    output = self._format_job_deletion_result(result)
                    return [TextContent(type="text", text=output)]

                elif name == "pause_job":
                    result = await pause_job_tool(self.config, arguments)
                    output = self._format_job_result(result, "Job Pause")
                    return [TextContent(type="text", text=output)]

                elif name == "resume_job":
                    result = await resume_job_tool(self.config, arguments)
                    output = self._format_job_result(result, "Job Resume")
                    return [TextContent(type="text", text=output)]

                elif name == "get_job_logs":
                    result = await get_job_logs_tool(self.config, arguments)
                    output = self._format_job_logs_result(result)
                    return [TextContent(type="text", text=output)]

                else:
                    error_msg = f"Unknown tool: {name}"
                    logger.error(error_msg)
                    return [TextContent(
                        type="text",
                        text=f"Error: {error_msg}"
                    )]

            except CronlyticError as e:
                error_msg = f"Cronlytic API error: {e.message}"
                logger.error(error_msg)
                return [TextContent(
                    type="text",
                    text=f"Error: {error_msg}\nDetails: {json.dumps(e.details, indent=2)}"
                )]

            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg, exc_info=True)
                return [TextContent(
                    type="text",
                    text=f"Error: {error_msg}"
                )]

        @self.server.list_resources()
        async def handle_list_resources() -> List[Resource]:
            """Handle list resources request."""
            logger.debug("Handling list_resources request")

            try:
                # Ensure we have configuration for job resources
                if self.config is None:
                    self.config = get_auth_config()

                # Initialize job resource provider if needed
                if self.job_resource_provider is None:
                    self.job_resource_provider = JobResourceProvider(self.config)

                # Get job resources
                job_resources = await self.job_resource_provider.get_resource_list()

                # Convert to MCP Resource objects
                resources = []
                for resource_data in job_resources:
                    resources.append(Resource(
                        uri=resource_data["uri"],
                        name=resource_data["name"],
                        description=resource_data.get("description", ""),
                        mimeType=resource_data.get("mimeType", "application/json")
                    ))

                # Add cron templates resource
                resources.append(Resource(
                    uri=self.cron_templates_provider.base_uri,
                    name="Cron Expression Templates",
                    description="Comprehensive collection of cron expression templates and patterns",
                    mimeType="application/json"
                ))

                logger.debug(f"Returning {len(resources)} resources")
                return resources

            except Exception as e:
                logger.error(f"Error listing resources: {e}")
                # Return at least the cron templates on error
                return [Resource(
                    uri=self.cron_templates_provider.base_uri,
                    name="Cron Expression Templates",
                    description="Comprehensive collection of cron expression templates and patterns",
                    mimeType="application/json"
                )]

        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Handle read resource request."""
            logger.debug(f"Handling read_resource request for URI: {uri}")

            try:
                if uri == self.cron_templates_provider.base_uri:
                    # Return cron templates
                    resource_data = self.cron_templates_provider.get_templates_resource()
                    return resource_data["text"]

                elif uri.startswith("cronlytic://"):
                    # Handle job resources
                    if self.config is None:
                        self.config = get_auth_config()

                    if self.job_resource_provider is None:
                        self.job_resource_provider = JobResourceProvider(self.config)

                    resource_data = await self.job_resource_provider.get_resource_content(uri)
                    return resource_data["text"]

                else:
                    raise ValueError(f"Unknown resource URI: {uri}")

            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                error_response = {
                    "error": "Failed to read resource",
                    "uri": uri,
                    "message": str(e)
                }
                return json.dumps(error_response, indent=2)

        @self.server.list_prompts()
        async def handle_list_prompts() -> List[Prompt]:
            """Handle list prompts request."""
            logger.debug("Handling list_prompts request")

            try:
                all_prompts = get_all_prompts()
                prompt_list = []

                for prompt_config in all_prompts:
                    arguments = []
                    for arg in prompt_config.get("arguments", []):
                        arguments.append(PromptArgument(
                            name=arg["name"],
                            description=arg["description"],
                            required=arg.get("required", False)
                        ))

                    prompt_list.append(Prompt(
                        name=prompt_config["name"],
                        description=prompt_config["description"],
                        arguments=arguments
                    ))

                logger.debug(f"Returning {len(prompt_list)} prompts")
                return prompt_list

            except Exception as e:
                logger.error(f"Error listing prompts: {e}")
                return []

        @self.server.get_prompt()
        async def handle_get_prompt(
            name: str, arguments: Optional[Dict[str, str]] = None
        ) -> GetPromptResult:
            """Handle get prompt request."""
            logger.debug(f"Handling get_prompt request for: {name}")

            try:
                all_prompts = get_all_prompts()

                # Find the requested prompt
                prompt_config = None
                for config in all_prompts:
                    if config["name"] == name:
                        prompt_config = config
                        break

                if not prompt_config:
                    raise ValueError(f"Prompt '{name}' not found")

                # Format the template with provided arguments
                template = prompt_config["template"]
                if arguments:
                    # Replace argument placeholders in the template
                    for arg_name, arg_value in arguments.items():
                        placeholder = "{" + arg_name + "}"
                        template = template.replace(placeholder, arg_value)

                # Create the prompt message
                message = PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=template)
                )

                return GetPromptResult(
                    description=prompt_config["description"],
                    messages=[message]
                )

            except Exception as e:
                logger.error(f"Error getting prompt '{name}': {e}")
                error_message = PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Error loading prompt '{name}': {str(e)}"
                    )
                )
                return GetPromptResult(
                    description=f"Error loading prompt: {name}",
                    messages=[error_message]
                )

    def _format_health_check_result(self, result: Dict[str, Any]) -> str:
        """Format health check result for display."""
        lines = [
            "# Cronlytic API Health Check",
            "",
            f"**Status:** {result.get('summary', 'Unknown')}",
            f"**Timestamp:** {result.get('timestamp', 'Unknown')}",
            f"**Response Time:** {result.get('response_time_ms', 'N/A')} ms",
            "",
            "## Connection Details",
            f"- **Base URL:** {result.get('base_url', 'Unknown')}",
            f"- **Connectivity:** {'✅' if result.get('connectivity') else '❌'}",
            f"- **Authentication:** {'✅' if result.get('authentication') else '❌'}",
            "",
        ]

        # Add job information if available
        details = result.get("details", {})
        if "job_count" in details:
            lines.extend([
                "## Job Information",
                f"- **Job Count:** {details['job_count']}",
                f"- **Can List Jobs:** {'✅' if details.get('can_list_jobs') else '❌'}",
                "",
            ])

        # Add performance info
        if "performance" in details:
            lines.extend([
                "## Performance",
                f"- **Performance Rating:** {details['performance'].title()}",
                "",
            ])

        # Add errors if any
        errors = result.get("errors", [])
        if errors:
            lines.extend([
                "## Errors",
                "",
            ])
            for error in errors:
                lines.append(f"- ❌ {error}")
            lines.append("")

        # Add recommendations
        recommendations = result.get("recommendations", [])
        if recommendations:
            lines.extend([
                "## Recommendations",
                "",
            ])
            for rec in recommendations:
                lines.append(f"- 💡 {rec}")
            lines.append("")

        # Add raw details for debugging
        if logger.isEnabledFor(logging.DEBUG):
            lines.extend([
                "## Debug Information",
                "```json",
                json.dumps(result, indent=2),
                "```",
            ])

        return "\n".join(lines)

    def _format_job_result(self, result: Dict[str, Any], operation: str) -> str:
        """Format job operation result for display."""
        lines = [f"# {operation} Result", ""]

        if result.get("success"):
            lines.append(f"✅ **Success:** {result.get('message', 'Operation completed')}")
            lines.append("")

            job = result.get("job")
            if job:
                lines.extend([
                    "## Job Details",
                    f"- **ID:** {job.get('id', 'N/A')}",
                    f"- **Name:** {job.get('name', 'N/A')}",
                    f"- **URL:** {job.get('url', 'N/A')}",
                    f"- **Method:** {job.get('method', 'N/A')}",
                    f"- **Cron Expression:** `{job.get('cron_expression', 'N/A')}`",
                    f"- **Status:** {job.get('status', 'N/A')}",
                    "",
                ])

                # Add next run time if available
                next_run = job.get("next_run_at") or result.get("next_run")
                if next_run:
                    lines.extend([
                        "## Schedule",
                        f"- **Next Run:** {next_run}",
                        "",
                    ])

                # Add headers if present
                headers = job.get("headers")
                if headers:
                    lines.extend([
                        "## Headers",
                    ])
                    for key, value in headers.items():
                        lines.append(f"- **{key}:** {value}")
                    lines.append("")

                # Add body if present
                body = job.get("body")
                if body:
                    lines.extend([
                        "## Request Body",
                        f"```",
                        body,
                        "```",
                        "",
                    ])

        else:
            lines.append(f"❌ **Error:** {result.get('message', 'Operation failed')}")
            lines.append("")

            # Add field-specific error if available
            field = result.get("field")
            value = result.get("value")
            if field and value is not None:
                lines.extend([
                    "## Validation Error",
                    f"- **Field:** {field}",
                    f"- **Value:** {value}",
                    "",
                ])

            # Add details if available
            details = result.get("details")
            if details:
                lines.extend([
                    "## Error Details",
                    "```json",
                    json.dumps(details, indent=2),
                    "```",
                    "",
                ])

        return "\n".join(lines)

    def _format_job_list_result(self, result: Dict[str, Any]) -> str:
        """Format job list result for display."""
        lines = ["# Job List", ""]

        if result.get("success"):
            summary = result.get("summary", {})
            total_count = summary.get("total_count", 0)

            lines.append(f"✅ **Found {total_count} job{'s' if total_count != 1 else ''}**")
            lines.append("")

            # Add summary statistics
            status_breakdown = summary.get("status_breakdown", {})
            if status_breakdown:
                lines.extend([
                    "## Status Summary",
                ])
                for status, count in status_breakdown.items():
                    emoji = "🟢" if status == "pending" else "⏸️" if status == "paused" else "🔵"
                    lines.append(f"- {emoji} **{status.title()}:** {count}")
                lines.append("")

            # Show if results were limited
            if summary.get("limited"):
                limit = summary.get("limit_applied")
                lines.extend([
                    f"⚠️ *Results limited to {limit} jobs*",
                    "",
                ])

            # List jobs
            jobs = result.get("jobs", [])
            if jobs:
                lines.extend([
                    "## Jobs",
                    "",
                ])

                for i, job in enumerate(jobs):
                    status = job.get("status", "unknown")
                    emoji = "🟢" if status == "pending" else "⏸️" if status == "paused" else "🔵"

                    lines.extend([
                        f"### {i+1}. {job.get('name', 'Unnamed Job')} {emoji}",
                        f"- **ID:** {job.get('id', 'N/A')}",
                        f"- **URL:** {job.get('url', 'N/A')}",
                        f"- **Method:** {job.get('method', 'N/A')}",
                        f"- **Cron:** `{job.get('cron_expression', 'N/A')}`",
                        f"- **Status:** {status}",
                    ])

                    next_run = job.get("next_run_at")
                    if next_run:
                        lines.append(f"- **Next Run:** {next_run}")

                    lines.append("")

            else:
                lines.extend([
                    "## No Jobs Found",
                    "",
                    "You haven't created any cron jobs yet. Use the `create_job` tool to get started!",
                    "",
                ])

        else:
            lines.append(f"❌ **Error:** {result.get('message', 'Failed to list jobs')}")
            lines.append("")

            # Add error details if available
            details = result.get("details")
            if details:
                lines.extend([
                    "## Error Details",
                    "```json",
                    json.dumps(details, indent=2),
                    "```",
                    "",
                ])

        return "\n".join(lines)

    def _format_job_deletion_result(self, result: Dict[str, Any]) -> str:
        """Format job deletion result for display."""
        lines = ["# Job Deletion Result", ""]

        if result.get("success"):
            lines.append(f"✅ **Success:** {result.get('message', 'Job deleted successfully')}")
            lines.append("")

            job_id = result.get("job_id")
            if job_id:
                lines.extend([
                    "## Deletion Details",
                    f"- **Job ID:** {job_id}",
                    f"- **Deleted:** {'Yes' if result.get('deleted') else 'No'}",
                ])

                deletion_time = result.get("deletion_timestamp")
                if deletion_time:
                    lines.append(f"- **Deletion Time:** {deletion_time}")

                lines.append("")

            lines.extend([
                "⚠️ **Important:** This action cannot be undone. The job and all its execution history have been permanently removed.",
                "",
            ])

        else:
            lines.append(f"❌ **Error:** {result.get('message', 'Failed to delete job')}")
            lines.append("")

            # Handle confirmation required case
            if result.get("error") == "Confirmation Required":
                lines.extend([
                    "## ⚠️ Confirmation Required",
                    "",
                    result.get("warning", "This action requires confirmation."),
                    "",
                    "**To proceed with deletion:**",
                    "- Set the `confirm` parameter to `true`",
                    "- **Warning:** This action cannot be undone!",
                    "",
                ])

            # Add field-specific error if available
            field = result.get("field")
            value = result.get("value")
            if field and value is not None:
                lines.extend([
                    "## Validation Error",
                    f"- **Field:** {field}",
                    f"- **Value:** {value}",
                    "",
                ])

            # Add details if available
            details = result.get("details")
            if details:
                lines.extend([
                    "## Error Details",
                    "```json",
                    json.dumps(details, indent=2),
                    "```",
                    "",
                ])

        return "\n".join(lines)

    def _format_job_logs_result(self, result: Dict[str, Any]) -> str:
        """Format job logs result for display."""
        lines = ["# Job Execution Logs", ""]

        if result.get("success"):
            summary = result.get("summary", {})
            total_logs = summary.get("total_logs_returned", 0)

            lines.append(f"✅ **{result.get('message', 'Logs retrieved successfully')}**")
            lines.append("")

            # Add summary statistics
            status_breakdown = summary.get("status_breakdown", {})
            if status_breakdown:
                lines.extend([
                    "## Execution Summary",
                ])
                for status, count in status_breakdown.items():
                    emoji = "✅" if status == "success" else "❌" if status == "failed" else "🔄" if status == "running" else "🔵"
                    lines.append(f"- {emoji} **{status.title()}:** {count}")
                lines.append("")

            # Show if results were limited
            if summary.get("limited"):
                limit = summary.get("limit_applied")
                lines.extend([
                    f"⚠️ *Results limited to {limit} log entries*",
                    "",
                ])

            # Display job information
            job_info = result.get("job", {})
            if job_info:
                lines.extend([
                    "## Job Information",
                    f"- **Name:** {job_info.get('name', 'N/A')}",
                    f"- **ID:** {job_info.get('id', 'N/A')}",
                    f"- **Status:** {job_info.get('status', 'N/A')}",
                    "",
                ])

            # List log entries
            logs = result.get("logs", [])
            if logs:
                lines.extend([
                    "## Recent Executions",
                    "",
                ])

                for i, log in enumerate(logs):
                    status = log.get("status", "unknown")
                    emoji = "✅" if status == "success" else "❌" if status == "failed" else "🔄" if status == "running" else "🔵"

                    lines.extend([
                        f"### {i+1}. Execution {emoji}",
                        f"- **Status:** {status}",
                    ])

                    # Add timestamp
                    timestamp = log.get("executed_at") or log.get("timestamp")
                    if timestamp:
                        lines.append(f"- **Executed At:** {timestamp}")

                    # Add duration if available
                    duration = log.get("duration_ms")
                    if duration is not None:
                        lines.append(f"- **Duration:** {duration}ms")

                    # Add response code if available
                    response_code = log.get("response_code")
                    if response_code is not None:
                        lines.append(f"- **Response Code:** {response_code}")

                    # Add response size if available
                    response_size = log.get("response_size")
                    if response_size is not None:
                        lines.append(f"- **Response Size:** {response_size} bytes")

                    # Add error message if failed
                    error_message = log.get("error") or log.get("error_message")
                    if error_message:
                        lines.extend([
                            f"- **Error:** {error_message}",
                        ])

                    # Add response body preview if available (truncated)
                    response_body = log.get("response_body")
                    if response_body and len(response_body) > 0:
                        preview = response_body[:200] + "..." if len(response_body) > 200 else response_body
                        lines.extend([
                            f"- **Response Preview:**",
                            f"  ```",
                            f"  {preview}",
                            f"  ```",
                        ])

                    lines.append("")

            else:
                lines.extend([
                    "## No Execution Logs Found",
                    "",
                    "This job hasn't been executed yet, or all log entries have expired.",
                    "",
                ])

        else:
            lines.append(f"❌ **Error:** {result.get('message', 'Failed to retrieve logs')}")
            lines.append("")

            # Add field-specific error if available
            field = result.get("field")
            value = result.get("value")
            if field and value is not None:
                lines.extend([
                    "## Validation Error",
                    f"- **Field:** {field}",
                    f"- **Value:** {value}",
                    "",
                ])

            # Add error details if available
            details = result.get("details")
            if details:
                lines.extend([
                    "## Error Details",
                    "```json",
                    json.dumps(details, indent=2),
                    "```",
                    "",
                ])

        return "\n".join(lines)

    async def run(self, transport_options: Optional[Dict[str, Any]] = None) -> None:
        """
        Run the MCP server.

        Args:
            transport_options: Optional transport configuration
        """
        try:
            # Load configuration if not provided
            if self.config is None:
                logger.info("Loading authentication configuration...")
                self.config = get_auth_config()
                logger.info("Authentication configuration loaded successfully")

            # Test connectivity during startup
            logger.info("Testing Cronlytic API connectivity...")
            async with CronlyticAPIClient(self.config) as test_client:
                health_result = await test_client.health_check()
                if health_result.get("status") == "healthy":
                    logger.info("✅ Cronlytic API connectivity test passed")
                else:
                    logger.warning("⚠️ Cronlytic API connectivity test failed")
                    logger.warning(f"Status: {health_result}")

            # Start the MCP server
            logger.info("Starting Cronlytic MCP Server...")

            # For Phase 1, we'll use stdio transport
            if transport_options is None:
                transport_options = {"type": "stdio"}

            # Run the server
            async with self.server.run_stdio():
                logger.info("Cronlytic MCP Server is running")
                # Keep the server running
                try:
                    while True:
                        await asyncio.sleep(1)
                except KeyboardInterrupt:
                    logger.info("Received shutdown signal")

        except Exception as e:
            logger.error(f"Failed to start server: {e}", exc_info=True)
            raise
        finally:
            logger.info("Cronlytic MCP Server stopped")

    async def shutdown(self) -> None:
        """Gracefully shutdown the server."""
        logger.info("Shutting down Cronlytic MCP Server...")

        if self.client:
            await self.client.close()

        logger.info("Shutdown complete")


async def main() -> None:
    """Main entry point for the server."""
    import argparse

    parser = argparse.ArgumentParser(description="Cronlytic MCP Server")
    parser.add_argument(
        "--config",
        help="Path to configuration file",
        type=str,
    )
    parser.add_argument(
        "--api-key",
        help="Cronlytic API key",
        type=str,
    )
    parser.add_argument(
        "--user-id",
        help="Cronlytic User ID",
        type=str,
    )
    parser.add_argument(
        "--base-url",
        help="Cronlytic API base URL",
        type=str,
        default="https://api.cronlytic.com/prog",
    )
    parser.add_argument(
        "--debug",
        help="Enable debug logging",
        action="store_true",
    )

    args = parser.parse_args()

    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.info("Debug logging enabled")

    try:
        # Get configuration
        config = get_auth_config(
            api_key=args.api_key,
            user_id=args.user_id,
            base_url=args.base_url,
            config_file=args.config,
        )

        # Create and run server
        server = CronlyticMCPServer(config)
        await server.run()

    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())