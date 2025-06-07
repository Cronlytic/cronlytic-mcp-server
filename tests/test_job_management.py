"""Unit tests for job management tools."""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from unittest.mock import AsyncMock, patch
from utils.auth import AuthConfig
from utils.errors import ValidationError, AuthenticationError, NotFoundError
from tools.job_management import create_job_tool, list_jobs_tool, get_job_tool


@pytest.fixture
def mock_config():
    """Mock authentication configuration."""
    return AuthConfig(
        api_key="test-api-key",
        user_id="test-user-id",
        base_url="https://api.cronlytic.com/prog",
    )


@pytest.fixture
def valid_job_data():
    """Valid job data for testing."""
    return {
        "name": "test-job",
        "url": "https://example.com/webhook",
        "method": "POST",
        "cron_expression": "0 12 * * *",
        "headers": {"Content-Type": "application/json"},
        "body": '{"test": true}',
    }


class TestCreateJobTool:
    """Test cases for create_job_tool."""

    @pytest.mark.asyncio
    async def test_create_job_success(self, mock_config, valid_job_data):
        """Test successful job creation."""
        expected_response = {
            "id": "job-123",
            "name": "test-job",
            "url": "https://example.com/webhook",
            "method": "POST",
            "cron_expression": "0 12 * * *",
            "status": "pending",
            "next_run_at": "2024-01-01T12:00:00Z",
        }

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_job.return_value = expected_response

            result = await create_job_tool(mock_config, valid_job_data)

            assert result["success"] is True
            assert result["job"]["id"] == "job-123"
            assert result["message"] == "Job 'test-job' created successfully"
            assert result["next_run"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_create_job_validation_error(self, mock_config):
        """Test job creation with validation error."""
        invalid_data = {
            "name": "invalid name!",  # Invalid characters
            "url": "not-a-url",  # Invalid URL
            "cron_expression": "invalid cron",  # Invalid cron
        }

        result = await create_job_tool(mock_config, invalid_data)

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert "field" in result

    @pytest.mark.asyncio
    async def test_create_job_api_error(self, mock_config, valid_job_data):
        """Test job creation with API error."""
        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_job.side_effect = AuthenticationError("Invalid API key")

            result = await create_job_tool(mock_config, valid_job_data)

            assert result["success"] is False
            assert result["error"] == "AuthenticationError"
            assert "Invalid API key" in result["message"]


class TestListJobsTool:
    """Test cases for list_jobs_tool."""

    @pytest.mark.asyncio
    async def test_list_jobs_success(self, mock_config):
        """Test successful job listing."""
        mock_jobs = [
            {
                "id": "job-1",
                "name": "job1",
                "url": "https://example.com/1",
                "method": "GET",
                "cron_expression": "0 12 * * *",
                "status": "pending",
                "next_run_at": "2024-01-01T12:00:00Z",
            },
            {
                "id": "job-2",
                "name": "job2",
                "url": "https://example.com/2",
                "method": "POST",
                "cron_expression": "*/5 * * * *",
                "status": "paused",
            },
        ]

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.list_jobs.return_value = mock_jobs

            result = await list_jobs_tool(mock_config, {})

            assert result["success"] is True
            assert len(result["jobs"]) == 2
            assert result["summary"]["total_count"] == 2
            assert result["summary"]["status_breakdown"]["pending"] == 1
            assert result["summary"]["status_breakdown"]["paused"] == 1

    @pytest.mark.asyncio
    async def test_list_jobs_with_filters(self, mock_config):
        """Test job listing with filters."""
        mock_jobs = [
            {"id": "job-1", "name": "job1", "status": "pending"},
            {"id": "job-2", "name": "job2", "status": "paused"},
            {"id": "job-3", "name": "job3", "status": "pending"},
        ]

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.list_jobs.return_value = mock_jobs

            # Test filtering out paused jobs
            result = await list_jobs_tool(mock_config, {"include_paused": False})

            assert result["success"] is True
            assert len(result["jobs"]) == 2  # Only pending jobs
            assert all(job["status"] == "pending" for job in result["jobs"])

    @pytest.mark.asyncio
    async def test_list_jobs_with_limit(self, mock_config):
        """Test job listing with limit."""
        mock_jobs = [{"id": f"job-{i}", "name": f"job{i}", "status": "pending"} for i in range(10)]

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.list_jobs.return_value = mock_jobs

            result = await list_jobs_tool(mock_config, {"limit": 5})

            assert result["success"] is True
            assert len(result["jobs"]) == 5
            assert result["summary"]["limited"] is True
            assert result["summary"]["limit_applied"] == 5

    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, mock_config):
        """Test listing jobs when none exist."""
        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.list_jobs.return_value = []

            result = await list_jobs_tool(mock_config, {})

            assert result["success"] is True
            assert len(result["jobs"]) == 0
            assert result["summary"]["total_count"] == 0
            assert result["message"] == "Found 0 jobs"


class TestGetJobTool:
    """Test cases for get_job_tool."""

    @pytest.mark.asyncio
    async def test_get_job_success(self, mock_config):
        """Test successful job retrieval."""
        mock_job = {
            "id": "job-123",
            "name": "test-job",
            "url": "https://example.com/webhook",
            "method": "POST",
            "cron_expression": "0 12 * * *",
            "status": "pending",
            "next_run_at": "2024-01-01T12:00:00Z",
            "headers": {"Content-Type": "application/json"},
            "body": '{"test": true}',
        }

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job.return_value = mock_job

            result = await get_job_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is True
            assert result["job"]["id"] == "job-123"
            assert result["job"]["name"] == "test-job"
            assert result["message"] == "Retrieved job 'test-job'"

    @pytest.mark.asyncio
    async def test_get_job_validation_error(self, mock_config):
        """Test job retrieval with invalid job ID."""
        result = await get_job_tool(mock_config, {"job_id": ""})

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"

    @pytest.mark.asyncio
    async def test_get_job_not_found(self, mock_config):
        """Test job retrieval when job doesn't exist."""
        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job.side_effect = NotFoundError("job", "job-123")

            result = await get_job_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is False
            assert result["error"] == "NotFoundError"

    @pytest.mark.asyncio
    async def test_get_job_missing_job_id(self, mock_config):
        """Test job retrieval without job_id parameter."""
        result = await get_job_tool(mock_config, {})

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"


# Integration-style tests (these would need actual API or better mocking)
class TestJobManagementIntegration:
    """Integration test cases for job management workflow."""

    @pytest.mark.asyncio
    async def test_create_then_get_job_workflow(self, mock_config, valid_job_data):
        """Test creating a job and then retrieving it."""
        created_job = {
            "id": "job-123",
            "name": "test-job",
            "url": "https://example.com/webhook",
            "method": "POST",
            "cron_expression": "0 12 * * *",
            "status": "pending",
            "next_run_at": "2024-01-01T12:00:00Z",
        }

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_job.return_value = created_job
            mock_client.get_job.return_value = created_job

            # Create job
            create_result = await create_job_tool(mock_config, valid_job_data)
            assert create_result["success"] is True
            job_id = create_result["job"]["id"]

            # Get job
            get_result = await get_job_tool(mock_config, {"job_id": job_id})
            assert get_result["success"] is True
            assert get_result["job"]["id"] == job_id
            assert get_result["job"]["name"] == "test-job"

    @pytest.mark.asyncio
    async def test_create_then_list_jobs_workflow(self, mock_config, valid_job_data):
        """Test creating a job and then seeing it in the list."""
        created_job = {
            "id": "job-123",
            "name": "test-job",
            "url": "https://example.com/webhook",
            "method": "POST",
            "cron_expression": "0 12 * * *",
            "status": "pending",
        }

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.create_job.return_value = created_job
            mock_client.list_jobs.return_value = [created_job]

            # Create job
            create_result = await create_job_tool(mock_config, valid_job_data)
            assert create_result["success"] is True

            # List jobs - should include the created job
            list_result = await list_jobs_tool(mock_config, {})
            assert list_result["success"] is True
            assert len(list_result["jobs"]) == 1
            assert list_result["jobs"][0]["id"] == "job-123"