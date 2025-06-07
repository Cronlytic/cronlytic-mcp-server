"""Tests for Phase 4 resources implementation."""

import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.resources.job_resources import JobResourceProvider
from src.resources.templates import CronTemplatesProvider
from src.utils.auth import AuthConfig


class TestJobResourceProvider:
    """Test cases for JobResourceProvider."""

    @pytest.fixture
    def mock_auth_config(self):
        """Create a mock auth config."""
        return AuthConfig(api_key="test-api-key-1234567890", user_id="12345678-1234-1234-1234-123456789012")

    @pytest.fixture
    def job_resource_provider(self, mock_auth_config):
        """Create a JobResourceProvider instance."""
        return JobResourceProvider(mock_auth_config)

    @pytest.fixture
    def sample_jobs(self):
        """Sample job data for testing."""
        return [
            {
                "job_id": "job-1",
                "name": "test-job-1",
                "url": "https://example.com/webhook1",
                "method": "GET",
                "status": "pending",
                "cron_expression": "*/5 * * * *",
                "next_run_at": "2025-01-01T12:00:00Z"
            },
            {
                "job_id": "job-2",
                "name": "test-job-2",
                "url": "https://example.com/webhook2",
                "method": "POST",
                "status": "paused",
                "cron_expression": "0 9 * * *",
                "next_run_at": None
            }
        ]

    @pytest.mark.asyncio
    async def test_get_resource_list_success(self, job_resource_provider, sample_jobs):
        """Test successful resource list retrieval."""
        with patch('src.resources.job_resources.CronlyticAPIClient') as mock_client:
            # Setup mock client
            mock_instance = AsyncMock()
            mock_instance.list_jobs.return_value = sample_jobs
            mock_client.return_value.__aenter__.return_value = mock_instance

            # Call the method
            resources = await job_resource_provider.get_resource_list()

            # Verify results
            assert isinstance(resources, list)
            assert len(resources) == 5  # 1 jobs list + 2 jobs + 2 logs

            # Check jobs list resource
            jobs_resource = resources[0]
            assert jobs_resource["uri"] == "cronlytic://jobs"
            assert jobs_resource["name"] == "All Jobs"
            assert "Live list of all user jobs" in jobs_resource["description"]
            assert jobs_resource["mimeType"] == "application/json"

            # Check individual job resources
            job_resources = [r for r in resources if r["uri"].startswith("cronlytic://job/") and "/logs" not in r["uri"]]
            assert len(job_resources) == 2

            job_1_resource = next(r for r in job_resources if "job-1" in r["uri"])
            assert job_1_resource["uri"] == "cronlytic://job/job-1"
            assert job_1_resource["name"] == "Job: test-job-1"

            # Check logs resources
            log_resources = [r for r in resources if r["uri"].endswith("/logs")]
            assert len(log_resources) == 2

            log_1_resource = next(r for r in log_resources if "job-1" in r["uri"])
            assert log_1_resource["uri"] == "cronlytic://job/job-1/logs"
            assert log_1_resource["name"] == "Logs: test-job-1"

    @pytest.mark.asyncio
    async def test_get_resource_list_api_error(self, job_resource_provider):
        """Test resource list when API fails."""
        with patch('src.resources.job_resources.CronlyticAPIClient') as mock_client:
            # Setup mock to raise exception
            mock_instance = AsyncMock()
            mock_instance.list_jobs.side_effect = Exception("API Error")
            mock_client.return_value.__aenter__.return_value = mock_instance

            # Call the method
            resources = await job_resource_provider.get_resource_list()

            # Should return basic resources even on error
            assert isinstance(resources, list)
            assert len(resources) == 1
            assert resources[0]["uri"] == "cronlytic://jobs"

    @pytest.mark.asyncio
    async def test_get_jobs_resource_content(self, job_resource_provider, sample_jobs):
        """Test jobs resource content."""
        with patch('src.resources.job_resources.CronlyticAPIClient') as mock_client:
            # Setup mock client
            mock_instance = AsyncMock()
            mock_instance.list_jobs.return_value = sample_jobs
            mock_client.return_value.__aenter__.return_value = mock_instance

            # Call the method
            result = await job_resource_provider.get_resource_content("cronlytic://jobs")

            # Verify result structure
            assert result["uri"] == "cronlytic://jobs"
            assert result["mimeType"] == "application/json"
            assert "text" in result

            # Parse the JSON content
            content = json.loads(result["text"])
            assert "summary" in content
            assert "jobs" in content
            assert "resource_info" in content

            # Check summary
            summary = content["summary"]
            assert summary["total_jobs"] == 2
            assert summary["active_jobs"] == 1
            assert summary["paused_jobs"] == 1
            assert summary["status_breakdown"]["pending"] == 1
            assert summary["status_breakdown"]["paused"] == 1

            # Check jobs data
            assert len(content["jobs"]) == 2
            assert content["jobs"] == sample_jobs

    @pytest.mark.asyncio
    async def test_get_single_job_resource_content(self, job_resource_provider):
        """Test single job resource content."""
        sample_job = {
            "job_id": "job-1",
            "name": "test-job",
            "url": "https://example.com/webhook",
            "method": "POST",
            "status": "pending",
            "cron_expression": "*/5 * * * *",
            "next_run_at": "2025-01-01T12:00:00Z"
        }

        with patch('src.resources.job_resources.CronlyticAPIClient') as mock_client:
            # Setup mock client
            mock_instance = AsyncMock()
            mock_instance.get_job.return_value = sample_job
            mock_client.return_value.__aenter__.return_value = mock_instance

            # Call the method
            result = await job_resource_provider.get_resource_content("cronlytic://job/job-1")

            # Verify result structure
            assert result["uri"] == "cronlytic://job/job-1"
            assert result["mimeType"] == "application/json"
            assert "text" in result

            # Parse the JSON content
            content = json.loads(result["text"])

            # Check enhanced job data
            assert content["job_id"] == "job-1"
            assert content["name"] == "test-job"
            assert "resource_info" in content
            assert "computed" in content

            # Check resource info
            resource_info = content["resource_info"]
            assert resource_info["uri"] == "cronlytic://job/job-1"
            assert resource_info["type"] == "job_details"

            # Check computed fields
            computed = content["computed"]
            assert computed["is_active"] is True
            assert computed["is_paused"] is False
            assert computed["has_next_run"] is True
            assert computed["execution_method"] == "POST https://example.com/webhook"

    @pytest.mark.asyncio
    async def test_get_job_logs_resource_content(self, job_resource_provider):
        """Test job logs resource content."""
        sample_logs = {
            "job_id": "job-1",
            "job": {"name": "test-job", "status": "pending"},
            "logs": [
                {
                    "timestamp": "2025-01-01T12:00:00Z",
                    "status": "success",
                    "response_code": 200,
                    "response_time": 0.123,
                    "error_message": ""
                },
                {
                    "timestamp": "2025-01-01T11:55:00Z",
                    "status": "failed",
                    "response_code": 500,
                    "response_time": 1.234,
                    "error_message": "Server error"
                }
            ]
        }

        with patch('src.resources.job_resources.CronlyticAPIClient') as mock_client:
            # Setup mock client
            mock_instance = AsyncMock()
            mock_instance.get_job_logs.return_value = sample_logs
            mock_client.return_value.__aenter__.return_value = mock_instance

            # Call the method
            result = await job_resource_provider.get_resource_content("cronlytic://job/job-1/logs")

            # Verify result structure
            assert result["uri"] == "cronlytic://job/job-1/logs"
            assert result["mimeType"] == "application/json"
            assert "text" in result

            # Parse the JSON content
            content = json.loads(result["text"])

            # Check structure
            assert "job_info" in content
            assert "summary" in content
            assert "logs" in content
            assert "resource_info" in content

            # Check job info
            job_info = content["job_info"]
            assert job_info["id"] == "job-1"
            assert job_info["name"] == "test-job"

            # Check summary
            summary = content["summary"]
            assert summary["total_executions"] == 2
            assert summary["status_breakdown"]["success"] == 1
            assert summary["status_breakdown"]["failed"] == 1
            assert summary["success_rate_percent"] == 50.0
            assert summary["has_recent_failures"] is True

            # Check logs
            assert len(content["logs"]) == 2
            assert content["logs"] == sample_logs["logs"]

    @pytest.mark.asyncio
    async def test_invalid_resource_uri(self, job_resource_provider):
        """Test handling of invalid resource URIs."""
        with pytest.raises(ValueError, match="Unsupported URI scheme"):
            await job_resource_provider.get_resource_content("http://invalid")

        with pytest.raises(ValueError, match="Unknown resource path"):
            await job_resource_provider.get_resource_content("cronlytic://invalid")

        with pytest.raises(ValueError, match="Invalid job resource path"):
            await job_resource_provider.get_resource_content("cronlytic://job/")

        with pytest.raises(ValueError, match="Invalid job resource path"):
            await job_resource_provider.get_resource_content("cronlytic://job/123/invalid")


class TestCronTemplatesProvider:
    """Test cases for CronTemplatesProvider."""

    @pytest.fixture
    def templates_provider(self):
        """Create a CronTemplatesProvider instance."""
        return CronTemplatesProvider()

    def test_initialization(self, templates_provider):
        """Test provider initialization."""
        assert templates_provider.base_uri == "cronlytic://templates/cron"
        assert templates_provider._templates is not None
        assert isinstance(templates_provider._templates, dict)

    def test_generate_templates_structure(self, templates_provider):
        """Test template structure and content."""
        templates = templates_provider._templates

        # Check main categories
        expected_categories = [
            "common_patterns",
            "weekly_patterns",
            "monthly_patterns",
            "special_patterns",
            "api_monitoring",
            "backup_schedules"
        ]

        for category in expected_categories:
            assert category in templates
            assert isinstance(templates[category], dict)

        # Check some specific templates
        assert "every_5_minutes" in templates["common_patterns"]
        assert "daily_midnight" in templates["common_patterns"]
        assert "weekly_monday" in templates["weekly_patterns"]
        assert "monthly_first" in templates["monthly_patterns"]

        # Verify template structure
        template = templates["common_patterns"]["every_5_minutes"]
        assert "expression" in template
        assert "description" in template
        assert "next_runs" in template
        assert "use_cases" in template
        assert template["expression"] == "*/5 * * * *"

    def test_get_templates_resource(self, templates_provider):
        """Test getting the templates resource."""
        result = templates_provider.get_templates_resource()

        # Check result structure
        assert result["uri"] == "cronlytic://templates/cron"
        assert result["mimeType"] == "application/json"
        assert "text" in result

        # Parse the JSON content
        content = json.loads(result["text"])

        # Check content structure
        assert "meta" in content
        assert "syntax_guide" in content
        assert "templates" in content
        assert "validation_tips" in content
        assert "resource_info" in content

        # Check meta information
        meta = content["meta"]
        assert "description" in meta
        assert "total_templates" in meta
        assert "categories" in meta
        assert "format" in meta
        assert "usage" in meta

        # Verify total templates count
        expected_total = sum(len(category) for category in templates_provider._templates.values())
        assert meta["total_templates"] == expected_total

        # Check syntax guide
        syntax_guide = content["syntax_guide"]
        assert "fields" in syntax_guide
        assert "special_characters" in syntax_guide
        assert "examples" in syntax_guide
        assert len(syntax_guide["fields"]) == 5  # 5-field cron

        # Check that all template categories are included
        assert content["templates"] == templates_provider._templates

        # Check validation tips
        assert isinstance(content["validation_tips"], list)
        assert len(content["validation_tips"]) > 0

    def test_template_content_quality(self, templates_provider):
        """Test that templates have high-quality content."""
        templates = templates_provider._templates

        for category_name, category in templates.items():
            assert isinstance(category, dict), f"Category {category_name} should be a dict"

            for template_name, template in category.items():
                # Check required fields
                assert "expression" in template, f"Template {template_name} missing expression"
                assert "description" in template, f"Template {template_name} missing description"
                assert "next_runs" in template, f"Template {template_name} missing next_runs"
                assert "use_cases" in template, f"Template {template_name} missing use_cases"

                # Check field types
                assert isinstance(template["expression"], str)
                assert isinstance(template["description"], str)
                assert isinstance(template["next_runs"], str)
                assert isinstance(template["use_cases"], list)

                # Check cron expression format (basic validation)
                expression = template["expression"]
                parts = expression.split()
                assert len(parts) == 5, f"Template {template_name} has invalid cron expression: {expression}"

                # Check use cases
                assert len(template["use_cases"]) > 0, f"Template {template_name} has no use cases"

    def test_specific_template_values(self, templates_provider):
        """Test specific template values for correctness."""
        templates = templates_provider._templates

        # Test some specific templates
        hourly = templates["common_patterns"]["hourly"]
        assert hourly["expression"] == "0 * * * *"
        assert "every hour" in hourly["description"].lower()

        daily = templates["common_patterns"]["daily_midnight"]
        assert daily["expression"] == "0 0 * * *"
        assert "midnight" in daily["description"].lower()

        weekly_monday = templates["weekly_patterns"]["weekly_monday"]
        assert weekly_monday["expression"] == "0 9 * * 1"
        assert "monday" in weekly_monday["description"].lower()

        monthly_first = templates["monthly_patterns"]["monthly_first"]
        assert monthly_first["expression"] == "0 9 1 * *"
        assert "1st" in monthly_first["description"]

    def test_api_monitoring_templates(self, templates_provider):
        """Test API monitoring specific templates."""
        api_templates = templates_provider._templates["api_monitoring"]

        # Check all expected monitoring templates
        expected_monitoring = ["high_frequency", "standard_monitoring", "light_monitoring"]
        for template_name in expected_monitoring:
            assert template_name in api_templates
            template = api_templates[template_name]
            assert "monitor" in template["description"].lower() or "monitoring" in template["description"].lower()

        # Verify frequencies make sense
        high_freq = api_templates["high_frequency"]["expression"]
        standard_freq = api_templates["standard_monitoring"]["expression"]
        light_freq = api_templates["light_monitoring"]["expression"]

        assert "*/2" in high_freq  # Every 2 minutes
        assert "*/5" in standard_freq  # Every 5 minutes
        assert "*/15" in light_freq  # Every 15 minutes

    def test_backup_schedule_templates(self, templates_provider):
        """Test backup schedule specific templates."""
        backup_templates = templates_provider._templates["backup_schedules"]

        # Check expected backup templates
        expected_backups = ["daily_backup", "weekly_backup", "incremental_backup"]
        for template_name in expected_backups:
            assert template_name in backup_templates
            template = backup_templates[template_name]
            assert "backup" in template["description"].lower()

        # Verify backup times (typically off-hours)
        daily = backup_templates["daily_backup"]["expression"]
        weekly = backup_templates["weekly_backup"]["expression"]

        assert "2" in daily  # 2 AM
        assert "3" in weekly  # 3 AM
        assert "0" in weekly  # Sunday (day 0)


@pytest.mark.asyncio
async def test_integration_resource_flow():
    """Test the complete resource flow integration."""
    # Mock auth config
    auth_config = AuthConfig(api_key="test-api-key-1234567890", user_id="12345678-1234-1234-1234-123456789012")

    # Test job resource provider
    job_provider = JobResourceProvider(auth_config)

    # Mock API client for integration test
    sample_jobs = [
        {
            "job_id": "integration-job",
            "name": "integration-test",
            "url": "https://test.com/webhook",
            "method": "GET",
            "status": "pending",
            "cron_expression": "*/10 * * * *"
        }
    ]

    with patch('src.resources.job_resources.CronlyticAPIClient') as mock_client:
        mock_instance = AsyncMock()
        mock_instance.list_jobs.return_value = sample_jobs
        mock_instance.get_job.return_value = sample_jobs[0]
        mock_instance.get_job_logs.return_value = {
            "job_id": "integration-job",
            "job": {"name": "integration-test", "status": "pending"},
            "logs": []
        }
        mock_client.return_value.__aenter__.return_value = mock_instance

        # Test resource list
        resources = await job_provider.get_resource_list()
        assert len(resources) == 3  # jobs list + 1 job + 1 logs

        # Test each resource content
        jobs_content = await job_provider.get_resource_content("cronlytic://jobs")
        assert "integration-job" in jobs_content["text"]

        job_content = await job_provider.get_resource_content("cronlytic://job/integration-job")
        assert "integration-test" in job_content["text"]

        logs_content = await job_provider.get_resource_content("cronlytic://job/integration-job/logs")
        assert "integration-job" in logs_content["text"]

    # Test templates provider
    templates_provider = CronTemplatesProvider()
    templates_content = templates_provider.get_templates_resource()
    assert "every_5_minutes" in templates_content["text"]
    assert "daily_midnight" in templates_content["text"]