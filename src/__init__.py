"""
Cronlytic MCP Server

A Model Context Protocol (MCP) server that provides tools, resources, and prompts
for managing cron jobs through the Cronlytic API.
"""

__version__ = "0.1.0"
__author__ = "Cronlytic Team"
__email__ = "saleh@cronlytic.com"

from .server import CronlyticMCPServer

__all__ = ["CronlyticMCPServer"]