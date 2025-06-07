"""Unit tests for Phase 3 tools: Advanced Job Management."""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pytest
from unittest.mock import AsyncMock, patch
from utils.auth import AuthConfig
from utils.errors import ValidationError, AuthenticationError, NotFoundError
from tools.job_management import update_job_tool, delete_job_tool
from tools.job_control import pause_job_tool, resume_job_tool, get_job_logs_tool


@pytest.fixture
def mock_config():
    """Mock authentication configuration."""
    return AuthConfig(
        api_key="test-api-key",
        user_id="test-user-id",
        base_url="https://api.cronlytic.com/prog",
    )


@pytest.fixture
def valid_update_data():
    """Valid job update data for testing."""
    return {
        "job_id": "job-123",
        "name": "updated-job",
        "url": "https://example.com/updated-webhook",
        "method": "PUT",
        "cron_expression": "0 6 * * *",
        "headers": {"Authorization": "Bearer token"},
        "body": '{"updated": true}',
    }


class TestUpdateJobTool:
    """Test cases for update_job_tool."""

    @pytest.mark.asyncio
    async def test_update_job_success(self, mock_config, valid_update_data):
        """Test successful job update."""
        expected_response = {
            "id": "job-123",
            "name": "updated-job",
            "url": "https://example.com/updated-webhook",
            "method": "PUT",
            "cron_expression": "0 6 * * *",
            "status": "pending",
            "next_run_at": "2024-01-01T06:00:00Z",
        }

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.update_job.return_value = expected_response

            result = await update_job_tool(mock_config, valid_update_data)

            assert result["success"] is True
            assert result["job"]["id"] == "job-123"
            assert result["job"]["name"] == "updated-job"
            assert result["message"] == "Job 'updated-job' updated successfully"
            assert result["changes_applied"] is True

    @pytest.mark.asyncio
    async def test_update_job_validation_error(self, mock_config):
        """Test job update with validation error."""
        invalid_data = {
            "job_id": "job-123",
            "name": "invalid name!",  # Invalid characters
            "url": "not-a-url",  # Invalid URL
            "cron_expression": "invalid cron",  # Invalid cron
        }

        result = await update_job_tool(mock_config, invalid_data)

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert "field" in result

    @pytest.mark.asyncio
    async def test_update_job_missing_job_id(self, mock_config):
        """Test job update without job_id."""
        invalid_data = {
            "name": "test-job",
            "url": "https://example.com/webhook",
            "cron_expression": "0 12 * * *",
        }

        result = await update_job_tool(mock_config, invalid_data)

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"

    @pytest.mark.asyncio
    async def test_update_job_api_error(self, mock_config, valid_update_data):
        """Test job update with API error."""
        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.update_job.side_effect = NotFoundError("job", "job-123")

            result = await update_job_tool(mock_config, valid_update_data)

            assert result["success"] is False
            assert result["error"] == "NotFoundError"


class TestDeleteJobTool:
    """Test cases for delete_job_tool."""

    @pytest.mark.asyncio
    async def test_delete_job_without_confirmation(self, mock_config):
        """Test job deletion without confirmation."""
        result = await delete_job_tool(mock_config, {"job_id": "job-123"})

        assert result["success"] is False
        assert result["error"] == "Confirmation Required"
        assert "Set 'confirm' parameter to true" in result["message"]
        assert "cannot be undone" in result["warning"]

    @pytest.mark.asyncio
    async def test_delete_job_with_confirmation_success(self, mock_config):
        """Test successful job deletion with confirmation."""
        mock_job_info = {"id": "job-123", "name": "test-job"}
        mock_deletion_result = {"deleted_at": "2024-01-01T12:00:00Z"}

        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job.return_value = mock_job_info
            mock_client.delete_job.return_value = mock_deletion_result

            result = await delete_job_tool(mock_config, {"job_id": "job-123", "confirm": True})

            assert result["success"] is True
            assert result["message"] == "Job 'test-job' has been permanently deleted"
            assert result["job_id"] == "job-123"
            assert result["deleted"] is True
            assert result["deletion_timestamp"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_delete_job_not_found(self, mock_config):
        """Test job deletion when job doesn't exist."""
        with patch("tools.job_management.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job.side_effect = NotFoundError("job", "job-123")
            mock_client.delete_job.side_effect = NotFoundError("job", "job-123")

            result = await delete_job_tool(mock_config, {"job_id": "job-123", "confirm": True})

            assert result["success"] is False
            assert result["error"] == "NotFoundError"

    @pytest.mark.asyncio
    async def test_delete_job_validation_error(self, mock_config):
        """Test job deletion with invalid job ID."""
        result = await delete_job_tool(mock_config, {"job_id": "", "confirm": True})

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"


class TestPauseJobTool:
    """Test cases for pause_job_tool."""

    @pytest.mark.asyncio
    async def test_pause_job_success(self, mock_config):
        """Test successful job pausing."""
        mock_job = {
            "id": "job-123",
            "name": "test-job",
            "status": "paused",
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.pause_job.return_value = mock_job

            result = await pause_job_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is True
            assert result["job"]["id"] == "job-123"
            assert result["message"] == "Job 'test-job' has been paused"
            assert result["status"] == "paused"

    @pytest.mark.asyncio
    async def test_pause_job_validation_error(self, mock_config):
        """Test job pausing with invalid job ID."""
        result = await pause_job_tool(mock_config, {"job_id": ""})

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"

    @pytest.mark.asyncio
    async def test_pause_job_api_error(self, mock_config):
        """Test job pausing with API error."""
        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.pause_job.side_effect = NotFoundError("job", "job-123")

            result = await pause_job_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is False
            assert result["error"] == "NotFoundError"


class TestResumeJobTool:
    """Test cases for resume_job_tool."""

    @pytest.mark.asyncio
    async def test_resume_job_success(self, mock_config):
        """Test successful job resuming."""
        mock_job = {
            "id": "job-123",
            "name": "test-job",
            "status": "pending",
            "next_run_at": "2024-01-01T12:00:00Z",
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.resume_job.return_value = mock_job

            result = await resume_job_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is True
            assert result["job"]["id"] == "job-123"
            assert result["message"] == "Job 'test-job' has been resumed"
            assert result["status"] == "pending"
            assert result["next_run"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_resume_job_validation_error(self, mock_config):
        """Test job resuming with invalid job ID."""
        result = await resume_job_tool(mock_config, {"job_id": ""})

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"

    @pytest.mark.asyncio
    async def test_resume_job_api_error(self, mock_config):
        """Test job resuming with API error."""
        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.resume_job.side_effect = NotFoundError("job", "job-123")

            result = await resume_job_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is False
            assert result["error"] == "NotFoundError"


class TestGetJobLogsTool:
    """Test cases for get_job_logs_tool."""

    @pytest.mark.asyncio
    async def test_get_job_logs_success(self, mock_config):
        """Test successful log retrieval."""
        mock_logs_data = {
            "job": {
                "id": "job-123",
                "name": "test-job",
                "status": "pending",
            },
            "logs": [
                {
                    "status": "success",
                    "executed_at": "2024-01-01T12:00:00Z",
                    "duration_ms": 150,
                    "response_code": 200,
                    "response_size": 1024,
                },
                {
                    "status": "failed",
                    "executed_at": "2024-01-01T11:00:00Z",
                    "duration_ms": 5000,
                    "response_code": 500,
                    "error_message": "Internal server error",
                },
            ],
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job_logs.return_value = mock_logs_data

            result = await get_job_logs_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is True
            assert len(result["logs"]) == 2
            assert result["job"]["name"] == "test-job"
            assert result["summary"]["total_logs_returned"] == 2
            assert result["summary"]["status_breakdown"]["success"] == 1
            assert result["summary"]["status_breakdown"]["failed"] == 1

    @pytest.mark.asyncio
    async def test_get_job_logs_with_limit(self, mock_config):
        """Test log retrieval with limit."""
        mock_logs_data = {
            "job": {"id": "job-123", "name": "test-job"},
            "logs": [{"status": "success"} for _ in range(50)],  # 50 log entries
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job_logs.return_value = mock_logs_data

            result = await get_job_logs_tool(mock_config, {"job_id": "job-123", "limit": 10})

            assert result["success"] is True
            assert len(result["logs"]) == 10
            assert result["summary"]["limited"] is True
            assert result["summary"]["limit_applied"] == 10

    @pytest.mark.asyncio
    async def test_get_job_logs_empty(self, mock_config):
        """Test log retrieval when no logs exist."""
        mock_logs_data = {
            "job": {"id": "job-123", "name": "test-job"},
            "logs": [],
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job_logs.return_value = mock_logs_data

            result = await get_job_logs_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is True
            assert len(result["logs"]) == 0
            assert result["summary"]["total_logs_returned"] == 0

    @pytest.mark.asyncio
    async def test_get_job_logs_validation_error(self, mock_config):
        """Test log retrieval with invalid job ID."""
        result = await get_job_logs_tool(mock_config, {"job_id": ""})

        assert result["success"] is False
        assert result["error"] == "Validation Error"
        assert result["field"] == "job_id"

    @pytest.mark.asyncio
    async def test_get_job_logs_api_error(self, mock_config):
        """Test log retrieval with API error."""
        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job_logs.side_effect = NotFoundError("job", "job-123")

            result = await get_job_logs_tool(mock_config, {"job_id": "job-123"})

            assert result["success"] is False
            assert result["error"] == "NotFoundError"

    @pytest.mark.asyncio
    async def test_get_job_logs_invalid_limit(self, mock_config):
        """Test log retrieval with invalid limit."""
        mock_logs_data = {
            "job": {"id": "job-123", "name": "test-job"},
            "logs": [{"status": "success"}],
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.get_job_logs.return_value = mock_logs_data

            # Test with invalid limit - should default to 20
            result = await get_job_logs_tool(mock_config, {"job_id": "job-123", "limit": 150})

            assert result["success"] is True
            # The tool should have corrected the invalid limit internally


# Integration-style tests for Phase 3 workflows
class TestPhase3Integration:
    """Integration test cases for Phase 3 workflow."""

    @pytest.mark.asyncio
    async def test_pause_then_resume_workflow(self, mock_config):
        """Test pausing and then resuming a job."""
        paused_job = {
            "id": "job-123",
            "name": "test-job",
            "status": "paused",
        }

        resumed_job = {
            "id": "job-123",
            "name": "test-job",
            "status": "pending",
            "next_run_at": "2024-01-01T12:00:00Z",
        }

        with patch("tools.job_control.CronlyticAPIClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.pause_job.return_value = paused_job
            mock_client.resume_job.return_value = resumed_job

            # Pause job
            pause_result = await pause_job_tool(mock_config, {"job_id": "job-123"})
            assert pause_result["success"] is True
            assert pause_result["status"] == "paused"

            # Resume job
            resume_result = await resume_job_tool(mock_config, {"job_id": "job-123"})
            assert resume_result["success"] is True
            assert resume_result["status"] == "pending"
            assert resume_result["next_run"] == "2024-01-01T12:00:00Z"

    @pytest.mark.asyncio
    async def test_update_then_get_logs_workflow(self, mock_config):
        """Test updating a job and then getting its logs."""
        updated_job = {
            "id": "job-123",
            "name": "updated-job",
            "status": "pending",
        }

        logs_data = {
            "job": updated_job,
            "logs": [{"status": "success", "executed_at": "2024-01-01T12:00:00Z"}],
        }

        update_data = {
            "job_id": "job-123",
            "name": "updated-job",
            "url": "https://example.com/webhook",
            "method": "GET",
            "cron_expression": "0 12 * * *",
            "headers": {},
            "body": "",
        }

        with patch("tools.job_management.CronlyticAPIClient") as mock_mgmt_client:
            with patch("tools.job_control.CronlyticAPIClient") as mock_ctrl_client:
                mock_mgmt = AsyncMock()
                mock_ctrl = AsyncMock()
                mock_mgmt_client.return_value.__aenter__.return_value = mock_mgmt
                mock_ctrl_client.return_value.__aenter__.return_value = mock_ctrl

                mock_mgmt.update_job.return_value = updated_job
                mock_ctrl.get_job_logs.return_value = logs_data

                # Update job
                update_result = await update_job_tool(mock_config, update_data)
                assert update_result["success"] is True
                assert update_result["job"]["name"] == "updated-job"

                # Get logs
                logs_result = await get_job_logs_tool(mock_config, {"job_id": "job-123"})
                assert logs_result["success"] is True
                assert len(logs_result["logs"]) == 1