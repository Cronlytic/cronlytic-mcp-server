"""Job resources for the Cronlytic MCP Server."""

import json
import logging
from typing import Any, Dict, List
from urllib.parse import urlparse

from cronlytic_client import CronlyticAPIClient
from utils.auth import AuthConfig
from utils.errors import CronlyticError


logger = logging.getLogger(__name__)


class JobResourceProvider:
    """Provider for job-related MCP resources."""

    def __init__(self, config: AuthConfig):
        """Initialize the job resource provider."""
        self.config = config
        self.base_uri = "cronlytic://"

    async def get_resource_list(self) -> List[Dict[str, Any]]:
        """Get list of available job resources."""
        try:
            # Get current jobs to provide dynamic resources
            async with CronlyticAPIClient(self.config) as client:
                jobs = await client.list_jobs()

            resources = [
                {
                    "uri": f"{self.base_uri}jobs",
                    "name": "All Jobs",
                    "description": "Live list of all user jobs with current status and configuration",
                    "mimeType": "application/json",
                }
            ]

            # Add individual job resources
            for job in jobs:
                job_id = job.get("job_id") or job.get("id")
                if job_id:
                    resources.extend([
                        {
                            "uri": f"{self.base_uri}job/{job_id}",
                            "name": f"Job: {job.get('name', job_id)}",
                            "description": f"Details for job '{job.get('name', job_id)}'",
                            "mimeType": "application/json",
                        },
                        {
                            "uri": f"{self.base_uri}job/{job_id}/logs",
                            "name": f"Logs: {job.get('name', job_id)}",
                            "description": f"Execution logs for job '{job.get('name', job_id)}'",
                            "mimeType": "application/json",
                        }
                    ])

            logger.debug(f"Generated {len(resources)} job resources")
            return resources

        except Exception as e:
            logger.error(f"Error getting job resource list: {e}")
            # Return basic resources even if we can't fetch jobs
            return [
                {
                    "uri": f"{self.base_uri}jobs",
                    "name": "All Jobs",
                    "description": "Live list of all user jobs",
                    "mimeType": "application/json",
                }
            ]

    async def get_resource_content(self, uri: str) -> Dict[str, Any]:
        """Get content for a specific resource URI."""
        try:
            parsed_uri = urlparse(uri)
            if parsed_uri.scheme != "cronlytic":
                raise ValueError(f"Unsupported URI scheme: {parsed_uri.scheme}")

            # Combine netloc and path to get the full resource identifier
            # cronlytic://jobs -> netloc="jobs", path=""
            # cronlytic://job/job-1 -> netloc="job", path="/job-1"
            # cronlytic://job/job-1/logs -> netloc="job", path="/job-1/logs"

            if parsed_uri.netloc == "jobs" and not parsed_uri.path:
                return await self._get_jobs_resource()
            elif parsed_uri.netloc == "job" and parsed_uri.path:
                # Remove leading slash and reconstruct the path
                job_path = parsed_uri.path.lstrip("/")
                return await self._get_job_resource(f"job/{job_path}")
            else:
                # Reconstruct full path for error message
                full_path = parsed_uri.netloc + parsed_uri.path
                raise ValueError(f"Unknown resource path: {full_path}")

        except Exception as e:
            logger.error(f"Error getting resource content for {uri}: {e}")
            raise

    async def _get_jobs_resource(self) -> Dict[str, Any]:
        """Get the jobs list resource content."""
        logger.debug("Fetching jobs list resource")

        async with CronlyticAPIClient(self.config) as client:
            jobs = await client.list_jobs()

        # Calculate summary statistics
        total_jobs = len(jobs)
        status_counts = {}
        active_jobs = 0
        paused_jobs = 0

        for job in jobs:
            status = job.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            if status == "pending":
                active_jobs += 1
            elif status == "paused":
                paused_jobs += 1

        return {
            "uri": "cronlytic://jobs",
            "mimeType": "application/json",
            "text": json.dumps({
                "summary": {
                    "total_jobs": total_jobs,
                    "active_jobs": active_jobs,
                    "paused_jobs": paused_jobs,
                    "status_breakdown": status_counts,
                },
                "jobs": jobs,
                "last_updated": "real-time",
                "resource_info": {
                    "description": "Live list of all user cron jobs",
                    "refresh_rate": "real-time",
                    "includes": ["job_details", "status", "next_run_time"]
                }
                        }, indent=2)
        }

    async def _get_job_resource(self, path: str) -> Dict[str, Any]:
        """Get individual job or job logs resource content."""
        path_parts = path.split("/")

        if len(path_parts) < 2:
            raise ValueError("Invalid job resource path")

        job_id = path_parts[1]

        # Validate that job_id is not empty
        if not job_id or job_id.strip() == "":
            raise ValueError("Invalid job resource path")

        if len(path_parts) == 2:
            # Individual job resource: cronlytic://job/{job_id}
            return await self._get_single_job_resource(job_id)
        elif len(path_parts) == 3 and path_parts[2] == "logs":
            # Job logs resource: cronlytic://job/{job_id}/logs
            return await self._get_job_logs_resource(job_id)
        else:
            raise ValueError(f"Invalid job resource path: {path}")

    async def _get_single_job_resource(self, job_id: str) -> Dict[str, Any]:
        """Get content for a single job resource."""
        logger.debug(f"Fetching job resource for ID: {job_id}")

        async with CronlyticAPIClient(self.config) as client:
            job = await client.get_job(job_id)

        # Enhance job data with additional information
        enhanced_job = dict(job)

        # Add resource metadata
        enhanced_job["resource_info"] = {
            "uri": f"cronlytic://job/{job_id}",
            "type": "job_details",
            "last_updated": "real-time",
            "description": f"Complete configuration and status for job '{job.get('name', job_id)}'"
        }

        # Add computed fields
        status = job.get("status", "unknown")
        enhanced_job["computed"] = {
            "is_active": status == "pending",
            "is_paused": status == "paused",
            "has_next_run": job.get("next_run_at") is not None,
            "execution_method": f"{job.get('method', 'GET')} {job.get('url', '')}"
        }

        return {
            "uri": f"cronlytic://job/{job_id}",
            "mimeType": "application/json",
            "text": json.dumps(enhanced_job, indent=2)
        }

    async def _get_job_logs_resource(self, job_id: str) -> Dict[str, Any]:
        """Get content for a job logs resource."""
        logger.debug(f"Fetching job logs resource for ID: {job_id}")

        async with CronlyticAPIClient(self.config) as client:
            logs_data = await client.get_job_logs(job_id)

        # Extract and enhance logs data
        logs = logs_data.get("logs", [])
        job_info = logs_data.get("job", {})

        # Calculate statistics
        total_logs = len(logs)
        status_counts = {}
        success_rate = 0

        for log in logs:
            status = log.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

        if total_logs > 0:
            success_count = status_counts.get("success", 0)
            success_rate = (success_count / total_logs) * 100

        enhanced_logs = {
            "job_info": {
                "id": job_id,
                "name": job_info.get("name", "Unknown"),
                "status": job_info.get("status", "unknown")
            },
            "summary": {
                "total_executions": total_logs,
                "status_breakdown": status_counts,
                "success_rate_percent": round(success_rate, 1),
                "has_recent_failures": status_counts.get("failed", 0) > 0
            },
            "logs": logs,
            "resource_info": {
                "uri": f"cronlytic://job/{job_id}/logs",
                "type": "execution_logs",
                "last_updated": "real-time",
                "description": f"Execution history for job '{job_info.get('name', job_id)}'",
                "log_count": total_logs,
                "retention": "Last 50 executions"
            }
        }

        return {
            "uri": f"cronlytic://job/{job_id}/logs",
            "mimeType": "application/json",
            "text": json.dumps(enhanced_logs, indent=2)
        }


# Export the provider class
__all__ = ["JobResourceProvider"]