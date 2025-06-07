"""Prompts package for the Cronlytic MCP Server."""

# Prompts will be implemented in Phase 5
# This file is a placeholder for the package structure

from .job_management import JobManagementPrompts
from .api_integration import APIIntegrationPrompts
from .troubleshooting import TroubleshootingPrompts
from .workflow_optimization import WorkflowOptimizationPrompts

__all__ = [
    "JobManagementPrompts",
    "APIIntegrationPrompts",
    "TroubleshootingPrompts",
    "WorkflowOptimizationPrompts",
    "get_all_prompts",
]


def get_all_prompts():
    """Get all available prompts from all categories."""
    all_prompts = []

    # Add job management prompts
    all_prompts.extend(JobManagementPrompts.get_prompts())

    # Add API integration prompts
    all_prompts.extend(APIIntegrationPrompts.get_prompts())

    # Add troubleshooting prompts
    all_prompts.extend(TroubleshootingPrompts.get_prompts())

    # Add workflow optimization prompts
    all_prompts.extend(WorkflowOptimizationPrompts.get_prompts())

    return all_prompts