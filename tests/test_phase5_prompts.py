"""Unit tests for Phase 5: Prompts & UX Implementation."""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from utils.auth import AuthConfig
from prompts import (
    JobManagementPrompts,
    APIIntegrationPrompts,
    TroubleshootingPrompts,
    WorkflowOptimizationPrompts,
    get_all_prompts
)
from server import CronlyticMCPServer


@pytest.fixture
def mock_config():
    """Mock authentication configuration."""
    return AuthConfig(
        api_key="test-api-key",
        user_id="test-user-id",
        base_url="https://api.cronlytic.com/prog",
    )


class TestJobManagementPrompts:
    """Test cases for job management prompts."""

    def test_get_prompts_returns_list(self):
        """Test that get_prompts returns a list of prompts."""
        prompts = JobManagementPrompts.get_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) > 0

        # Check that all items are dictionaries with required keys
        for prompt in prompts:
            assert isinstance(prompt, dict)
            assert "name" in prompt
            assert "description" in prompt
            assert "template" in prompt

    def test_create_job_prompt_structure(self):
        """Test the structure of the create job prompt."""
        prompts = JobManagementPrompts.get_prompts()
        create_prompt = next((p for p in prompts if p["name"] == "create_job_flow"), None)

        assert create_prompt is not None
        assert create_prompt["description"] == "Interactive flow to create a new cron job with step-by-step guidance"
        assert "arguments" in create_prompt
        assert isinstance(create_prompt["arguments"], list)

        # Check arguments structure
        for arg in create_prompt["arguments"]:
            assert "name" in arg
            assert "description" in arg
            assert "required" in arg

    def test_update_job_prompt_structure(self):
        """Test the structure of the update job prompt."""
        prompts = JobManagementPrompts.get_prompts()
        update_prompt = next((p for p in prompts if p["name"] == "update_job_flow"), None)

        assert update_prompt is not None
        assert "job_id" in [arg["name"] for arg in update_prompt["arguments"]]
        assert "update_type" in [arg["name"] for arg in update_prompt["arguments"]]

    def test_monitoring_prompt_structure(self):
        """Test the structure of the monitoring prompt."""
        prompts = JobManagementPrompts.get_prompts()
        monitoring_prompt = next((p for p in prompts if p["name"] == "job_monitoring_dashboard"), None)

        assert monitoring_prompt is not None
        assert "time_range" in [arg["name"] for arg in monitoring_prompt["arguments"]]
        assert "focus_area" in [arg["name"] for arg in monitoring_prompt["arguments"]]

    def test_troubleshooting_prompt_structure(self):
        """Test the structure of the troubleshooting prompt."""
        prompts = JobManagementPrompts.get_prompts()
        troubleshooting_prompt = next((p for p in prompts if p["name"] == "job_troubleshooting_guide"), None)

        assert troubleshooting_prompt is not None
        assert "issue_type" in [arg["name"] for arg in troubleshooting_prompt["arguments"]]

    def test_bulk_operations_prompt_structure(self):
        """Test the structure of the bulk operations prompt."""
        prompts = JobManagementPrompts.get_prompts()
        bulk_prompt = next((p for p in prompts if p["name"] == "bulk_job_operations"), None)

        assert bulk_prompt is not None
        assert "operation_type" in [arg["name"] for arg in bulk_prompt["arguments"]]
        assert "job_filter" in [arg["name"] for arg in bulk_prompt["arguments"]]

    def test_prompt_names_exist(self):
        """Test that expected prompt names exist."""
        prompts = JobManagementPrompts.get_prompts()
        prompt_names = [p["name"] for p in prompts]

        expected_names = [
            "create_job_flow",
            "update_job_flow",
            "job_monitoring_dashboard",
            "job_troubleshooting_guide",
            "bulk_job_operations"
        ]

        for name in expected_names:
            assert name in prompt_names


class TestAPIIntegrationPrompts:
    """Test cases for API integration prompts."""

    def test_get_prompts_returns_list(self):
        """Test that get_prompts returns a list of prompts."""
        prompts = APIIntegrationPrompts.get_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) > 0

    def test_setup_configuration_prompt(self):
        """Test the setup configuration prompt."""
        prompts = APIIntegrationPrompts.get_prompts()
        setup_prompt = next((p for p in prompts if p["name"] == "setup_configuration"), None)

        assert setup_prompt is not None
        assert "setup_stage" in [arg["name"] for arg in setup_prompt["arguments"]]
        assert "environment" in [arg["name"] for arg in setup_prompt["arguments"]]

    def test_authentication_guide_prompt(self):
        """Test the authentication guide prompt."""
        prompts = APIIntegrationPrompts.get_prompts()
        auth_prompt = next((p for p in prompts if p["name"] == "authentication_guide"), None)

        assert auth_prompt is not None
        assert "auth_issue" in [arg["name"] for arg in auth_prompt["arguments"]]

    def test_claude_desktop_integration_prompt(self):
        """Test the Claude Desktop integration prompt."""
        prompts = APIIntegrationPrompts.get_prompts()
        claude_prompt = next((p for p in prompts if p["name"] == "claude_desktop_integration"), None)

        assert claude_prompt is not None
        assert "integration_step" in [arg["name"] for arg in claude_prompt["arguments"]]
        assert "operating_system" in [arg["name"] for arg in claude_prompt["arguments"]]

    def test_webhook_testing_prompt(self):
        """Test the webhook testing guide prompt."""
        prompts = APIIntegrationPrompts.get_prompts()
        webhook_prompt = next((p for p in prompts if p["name"] == "webhook_testing_guide"), None)

        assert webhook_prompt is not None
        assert "test_type" in [arg["name"] for arg in webhook_prompt["arguments"]]

    def test_api_troubleshooting_prompt(self):
        """Test the API troubleshooting prompt."""
        prompts = APIIntegrationPrompts.get_prompts()
        api_troubleshooting = next((p for p in prompts if p["name"] == "api_troubleshooting_guide"), None)

        assert api_troubleshooting is not None
        assert "problem_type" in [arg["name"] for arg in api_troubleshooting["arguments"]]

    def test_expected_prompts_exist(self):
        """Test that expected API integration prompts exist."""
        prompts = APIIntegrationPrompts.get_prompts()
        prompt_names = [p["name"] for p in prompts]

        expected_names = [
            "setup_configuration",
            "authentication_guide",
            "claude_desktop_integration",
            "webhook_testing_guide",
            "api_troubleshooting_guide"
        ]

        for name in expected_names:
            assert name in prompt_names


class TestTroubleshootingPrompts:
    """Test cases for troubleshooting prompts."""

    def test_get_prompts_returns_list(self):
        """Test that get_prompts returns a list of prompts."""
        prompts = TroubleshootingPrompts.get_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) > 0

    def test_system_diagnostics_prompt(self):
        """Test the system diagnostics prompt."""
        prompts = TroubleshootingPrompts.get_prompts()
        diagnostics_prompt = next((p for p in prompts if p["name"] == "system_diagnostics"), None)

        assert diagnostics_prompt is not None
        assert "diagnostic_level" in [arg["name"] for arg in diagnostics_prompt["arguments"]]
        assert "focus_area" in [arg["name"] for arg in diagnostics_prompt["arguments"]]

    def test_error_analysis_prompt(self):
        """Test the error analysis prompt."""
        prompts = TroubleshootingPrompts.get_prompts()
        error_prompt = next((p for p in prompts if p["name"] == "error_analysis_guide"), None)

        assert error_prompt is not None
        assert "error_type" in [arg["name"] for arg in error_prompt["arguments"]]

    def test_performance_optimization_prompt(self):
        """Test the performance optimization prompt."""
        prompts = TroubleshootingPrompts.get_prompts()
        perf_prompt = next((p for p in prompts if p["name"] == "performance_optimization"), None)

        assert perf_prompt is not None
        assert "optimization_focus" in [arg["name"] for arg in perf_prompt["arguments"]]

    def test_maintenance_guide_prompt(self):
        """Test the maintenance guide prompt."""
        prompts = TroubleshootingPrompts.get_prompts()
        maintenance_prompt = next((p for p in prompts if p["name"] == "maintenance_guide"), None)

        assert maintenance_prompt is not None
        assert "maintenance_type" in [arg["name"] for arg in maintenance_prompt["arguments"]]

    def test_expected_prompts_exist(self):
        """Test that expected troubleshooting prompts exist."""
        prompts = TroubleshootingPrompts.get_prompts()
        prompt_names = [p["name"] for p in prompts]

        expected_names = [
            "system_diagnostics",
            "error_analysis_guide",
            "performance_optimization",
            "maintenance_guide"
        ]

        for name in expected_names:
            assert name in prompt_names


class TestWorkflowOptimizationPrompts:
    """Test cases for workflow optimization prompts."""

    def test_get_prompts_returns_list(self):
        """Test that get_prompts returns a list of prompts."""
        prompts = WorkflowOptimizationPrompts.get_prompts()

        assert isinstance(prompts, list)
        assert len(prompts) > 0

    def test_best_practices_prompt(self):
        """Test the best practices prompt."""
        prompts = WorkflowOptimizationPrompts.get_prompts()
        best_practices = next((p for p in prompts if p["name"] == "best_practices_guide"), None)

        assert best_practices is not None
        assert "practice_area" in [arg["name"] for arg in best_practices["arguments"]]
        assert "experience_level" in [arg["name"] for arg in best_practices["arguments"]]

    def test_schedule_optimization_prompt(self):
        """Test the schedule optimization prompt."""
        prompts = WorkflowOptimizationPrompts.get_prompts()
        schedule_prompt = next((p for p in prompts if p["name"] == "schedule_optimization"), None)

        assert schedule_prompt is not None
        assert "optimization_goal" in [arg["name"] for arg in schedule_prompt["arguments"]]

    def test_automation_strategies_prompt(self):
        """Test the automation strategies prompt."""
        prompts = WorkflowOptimizationPrompts.get_prompts()
        automation_prompt = next((p for p in prompts if p["name"] == "automation_strategies"), None)

        assert automation_prompt is not None
        assert "automation_scope" in [arg["name"] for arg in automation_prompt["arguments"]]

    def test_scaling_strategies_prompt(self):
        """Test the scaling strategies prompt."""
        prompts = WorkflowOptimizationPrompts.get_prompts()
        scaling_prompt = next((p for p in prompts if p["name"] == "scaling_strategies"), None)

        assert scaling_prompt is not None
        assert "growth_scenario" in [arg["name"] for arg in scaling_prompt["arguments"]]

    def test_expected_prompts_exist(self):
        """Test that expected workflow prompts exist."""
        prompts = WorkflowOptimizationPrompts.get_prompts()
        prompt_names = [p["name"] for p in prompts]

        expected_names = [
            "best_practices_guide",
            "schedule_optimization",
            "automation_strategies",
            "scaling_strategies"
        ]

        for name in expected_names:
            assert name in prompt_names


class TestPromptIntegration:
    """Test cases for prompt integration functionality."""

    def test_get_all_prompts_aggregation(self):
        """Test that get_all_prompts aggregates all prompt categories."""
        all_prompts = get_all_prompts()

        assert isinstance(all_prompts, list)
        assert len(all_prompts) >= 16  # Minimum expected prompts

        # Verify we have prompts from all categories
        prompt_names = [p["name"] for p in all_prompts]

        # Check for job management prompts
        assert "create_job_flow" in prompt_names
        assert "update_job_flow" in prompt_names

        # Check for API integration prompts
        assert "setup_configuration" in prompt_names
        assert "authentication_guide" in prompt_names

        # Check for troubleshooting prompts
        assert "system_diagnostics" in prompt_names
        assert "error_analysis_guide" in prompt_names

        # Check for workflow optimization prompts
        assert "best_practices_guide" in prompt_names
        assert "schedule_optimization" in prompt_names

    def test_prompt_uniqueness(self):
        """Test that all prompt names are unique."""
        all_prompts = get_all_prompts()
        prompt_names = [p["name"] for p in all_prompts]

        # Check for duplicates
        assert len(prompt_names) == len(set(prompt_names)), "Duplicate prompt names found"

    def test_prompt_structure_validity(self):
        """Test that all prompts have valid structure."""
        all_prompts = get_all_prompts()

        for prompt in all_prompts:
            # Required fields
            assert "name" in prompt
            assert "description" in prompt
            assert "template" in prompt

            # Type validation
            assert isinstance(prompt["name"], str)
            assert isinstance(prompt["description"], str)
            assert isinstance(prompt["template"], str)

            # Content validation
            assert len(prompt["name"]) > 0
            assert len(prompt["description"]) > 10
            assert len(prompt["template"]) > 100

            # Arguments validation if present
            if "arguments" in prompt:
                assert isinstance(prompt["arguments"], list)
                for arg in prompt["arguments"]:
                    assert "name" in arg
                    assert "description" in arg
                    assert "required" in arg


class TestPromptQuality:
    """Test cases for prompt content quality."""

    def test_prompt_templates_are_comprehensive(self):
        """Test that prompt templates contain substantial content."""
        all_prompts = get_all_prompts()

        for prompt in all_prompts:
            template = prompt["template"]

            # Check for markdown structure
            assert "# " in template  # Has main title
            assert "## " in template  # Has subsections

            # Check minimum content length
            assert len(template) > 500  # Substantial content

            # Check for interactive elements
            assert any(marker in template for marker in ["**", "- ", "✅", "❌", "🔧", "📊"])

    def test_prompt_descriptions_are_clear(self):
        """Test that prompt descriptions are clear and helpful."""
        all_prompts = get_all_prompts()

        for prompt in all_prompts:
            description = prompt["description"]
            assert len(description) > 20  # Substantial description
            assert description[0].isupper()  # Proper capitalization
            # Should describe what the prompt does
            assert any(word in description.lower() for word in ["guide", "flow", "assistance", "help"])

    def test_prompts_have_practical_content(self):
        """Test that prompts contain practical, actionable content."""
        all_prompts = get_all_prompts()

        for prompt in all_prompts:
            template = prompt["template"].lower()

            # Should have actionable elements
            practical_indicators = [
                "step", "example", "command", "action", "how to",
                "ready to", "tell me", "help you", "guide you"
            ]

            assert any(indicator in template for indicator in practical_indicators)


class TestMCPServerIntegration:
    """Test cases for MCP server integration."""

    def test_server_initializes_with_prompts(self, mock_config):
        """Test that MCP server initializes properly with prompts."""
        server = CronlyticMCPServer(mock_config)

        # Server should initialize without errors
        assert server is not None
        assert server.server is not None

    def test_prompt_imports_work(self):
        """Test that all prompt imports work correctly."""
        # Test individual imports
        job_prompts = JobManagementPrompts.get_prompts()
        api_prompts = APIIntegrationPrompts.get_prompts()
        troubleshooting_prompts = TroubleshootingPrompts.get_prompts()
        workflow_prompts = WorkflowOptimizationPrompts.get_prompts()

        assert len(job_prompts) > 0
        assert len(api_prompts) > 0
        assert len(troubleshooting_prompts) > 0
        assert len(workflow_prompts) > 0

        # Test aggregate import
        all_prompts = get_all_prompts()
        expected_total = len(job_prompts) + len(api_prompts) + len(troubleshooting_prompts) + len(workflow_prompts)
        assert len(all_prompts) == expected_total


class TestPromptArgumentHandling:
    """Test cases for prompt argument handling."""

    def test_arguments_have_valid_structure(self):
        """Test that all prompt arguments have valid structure."""
        all_prompts = get_all_prompts()

        for prompt in all_prompts:
            if "arguments" in prompt:
                for arg in prompt["arguments"]:
                    assert isinstance(arg, dict)
                    assert "name" in arg
                    assert "description" in arg
                    assert "required" in arg

                    assert isinstance(arg["name"], str)
                    assert isinstance(arg["description"], str)
                    assert isinstance(arg["required"], bool)

                    assert len(arg["name"]) > 0
                    assert len(arg["description"]) > 5

    def test_template_placeholders_match_arguments(self):
        """Test that template placeholders match defined arguments."""
        all_prompts = get_all_prompts()

        for prompt in all_prompts:
            template = prompt["template"]
            arguments = prompt.get("arguments", [])

            # Extract placeholders from template
            import re
            placeholders = re.findall(r'\{(\w+)\}', template)
            arg_names = [arg["name"] for arg in arguments]

            # All placeholders should have corresponding arguments
            for placeholder in placeholders:
                assert placeholder in arg_names, f"Placeholder '{placeholder}' not in arguments for prompt '{prompt['name']}'"


class TestUserExperience:
    """Test cases for user experience aspects."""

    def test_prompts_cover_user_journey(self):
        """Test that prompts cover the complete user journey."""
        all_prompts = get_all_prompts()
        prompt_names = [p["name"] for p in all_prompts]

        # Setup journey
        assert "setup_configuration" in prompt_names
        assert "authentication_guide" in prompt_names
        assert "claude_desktop_integration" in prompt_names

        # Usage journey
        assert "create_job_flow" in prompt_names
        assert "job_monitoring_dashboard" in prompt_names
        assert "update_job_flow" in prompt_names

        # Troubleshooting journey
        assert "job_troubleshooting_guide" in prompt_names
        assert "system_diagnostics" in prompt_names

        # Optimization journey
        assert "best_practices_guide" in prompt_names
        assert "performance_optimization" in prompt_names

    def test_prompts_provide_progressive_complexity(self):
        """Test that prompts support users at different skill levels."""
        all_prompts = get_all_prompts()

        # Should have basic setup guides
        basic_prompts = ["setup_configuration", "authentication_guide", "create_job_flow"]
        prompt_names = [p["name"] for p in all_prompts]

        for basic_prompt in basic_prompts:
            assert basic_prompt in prompt_names

        # Should have advanced optimization guides
        advanced_prompts = ["automation_strategies", "scaling_strategies", "performance_optimization"]

        for advanced_prompt in advanced_prompts:
            assert advanced_prompt in prompt_names

    def test_error_scenarios_are_covered(self):
        """Test that error and troubleshooting scenarios are well covered."""
        all_prompts = get_all_prompts()

        troubleshooting_coverage = [
            "job_troubleshooting_guide",
            "api_troubleshooting_guide",
            "error_analysis_guide",
            "system_diagnostics"
        ]

        prompt_names = [p["name"] for p in all_prompts]

        for troubleshooting_prompt in troubleshooting_coverage:
            assert troubleshooting_prompt in prompt_names