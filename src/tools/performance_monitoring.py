"""Performance monitoring tools for the Cronlytic MCP Server."""

import json
import logging
from typing import Any, Dict

from utils.performance import get_performance_report


logger = logging.getLogger(__name__)


# Tool definition
PERFORMANCE_REPORT_TOOL_DEFINITION = {
    "name": "get_performance_report",
    "description": "Get comprehensive performance metrics and monitoring data for the MCP server",
    "inputSchema": {
        "type": "object",
        "properties": {
            "include_details": {
                "type": "boolean",
                "default": True,
                "description": "Include detailed metrics for each operation",
            },
            "format": {
                "type": "string",
                "enum": ["summary", "detailed", "json"],
                "default": "detailed",
                "description": "Format of the performance report",
            },
        },
        "additionalProperties": False,
    },
}


async def get_performance_report_tool(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get performance monitoring report.

    Args:
        arguments: Tool arguments containing report options

    Returns:
        Dict containing performance metrics and monitoring data
    """
    logger.info("Generating performance report")
    logger.debug(f"Report arguments: {arguments}")

    try:
        # Get optional parameters
        include_details = arguments.get("include_details", True)
        report_format = arguments.get("format", "detailed")

        # Generate performance report
        report = get_performance_report()

        if report_format == "json":
            # Return raw JSON format
            return {
                "success": True,
                "report": report,
                "format": "json",
            }

        elif report_format == "summary":
            # Return summary format
            summary = report.get("summary", {})
            return {
                "success": True,
                "summary": {
                    "total_operations": summary.get("total_operations", 0),
                    "total_errors": summary.get("total_errors", 0),
                    "success_rate": f"{summary.get('overall_success_rate', 0):.1f}%",
                    "monitored_operations": summary.get("monitored_operations", 0),
                },
                "timestamp": report.get("timestamp"),
                "format": "summary",
            }

        else:
            # Return detailed format (default)
            summary = report.get("summary", {})
            detailed = report.get("detailed_metrics", {}) if include_details else {}

            # Format slowest operations
            slowest_ops = summary.get("slowest_operations", [])
            slowest_formatted = [
                f"{name}: {time:.3f}s avg" for name, time in slowest_ops
            ]

            # Format most used operations
            most_used_ops = summary.get("most_used_operations", [])
            most_used_formatted = [
                f"{name}: {count} calls" for name, count in most_used_ops
            ]

            result = {
                "success": True,
                "performance_summary": {
                    "total_operations": summary.get("total_operations", 0),
                    "total_errors": summary.get("total_errors", 0),
                    "overall_success_rate": f"{summary.get('overall_success_rate', 0):.1f}%",
                    "monitored_operations": summary.get("monitored_operations", 0),
                    "slowest_operations": slowest_formatted[:5],
                    "most_used_operations": most_used_formatted[:5],
                },
                "timestamp": report.get("timestamp"),
                "format": "detailed",
            }

            if include_details and detailed:
                result["detailed_metrics"] = detailed

            return result

    except Exception as e:
        logger.error(f"Error generating performance report: {e}", exc_info=True)
        return {
            "success": False,
            "error": "Performance Report Error",
            "message": str(e),
        }