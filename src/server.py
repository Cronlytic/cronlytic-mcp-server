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
    ListToolsRequest,
    ListToolsResult,
    Resource,
    Tool,
    TextContent,
)
from cronlytic_client import CronlyticAPIClient
from tools.health_check import health_check_tool, HEALTH_CHECK_TOOL_DEFINITION
from utils.auth import AuthConfig, get_auth_config
from utils.errors import CronlyticError


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
                Tool(
                    name=HEALTH_CHECK_TOOL_DEFINITION["name"],
                    description=HEALTH_CHECK_TOOL_DEFINITION["description"],
                    inputSchema=HEALTH_CHECK_TOOL_DEFINITION["inputSchema"],
                )
            ]

            logger.debug(f"Returning {len(tools)} tools")
            return tools

        @self.server.call_tool()
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

                    # Format result as readable text
                    output = self._format_health_check_result(result)

                    return [TextContent(
                        type="text",
                        text=output
                    )]

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