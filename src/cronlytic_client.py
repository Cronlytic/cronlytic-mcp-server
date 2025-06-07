"""Cronlytic API client wrapper for the MCP server."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import aiohttp
from aiohttp import ClientTimeout, ClientConnectorError, ClientResponseError

from .utils.auth import AuthConfig
from .utils.errors import (
    APIError,
    AuthenticationError,
    AuthorizationError,
    ConnectionError,
    NotFoundError,
    RateLimitError,
    TimeoutError,
)

logger = logging.getLogger(__name__)


class CronlyticAPIClient:
    """
    Async HTTP client for the Cronlytic API.

    Provides methods for all Cronlytic API operations with proper error handling,
    retry logic, and connection management.
    """

    def __init__(self, config: AuthConfig) -> None:
        """
        Initialize the Cronlytic API client.

        Args:
            config: Authentication and configuration settings
        """
        self.config = config
        self.session: Optional[aiohttp.ClientSession] = None
        self._closed = False

    async def __aenter__(self) -> "CronlyticAPIClient":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def connect(self) -> None:
        """Initialize the HTTP session."""
        if self.session is None or self.session.closed:
            timeout = ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)

            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=self.config.get_headers(),
            )
            self._closed = False
            logger.debug("Cronlytic API client session initialized")

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self._closed = True
            logger.debug("Cronlytic API client session closed")

    def _get_url(self, endpoint: str) -> str:
        """Get full URL for an endpoint."""
        return f"{self.config.base_url}/{endpoint.lstrip('/')}"

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request with error handling and retries.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data (for POST/PUT)
            params: Query parameters

        Returns:
            Dict containing the response data

        Raises:
            ConnectionError: If connection fails
            AuthenticationError: If authentication fails
            AuthorizationError: If authorization fails
            NotFoundError: If resource not found
            APIError: For other API errors
            TimeoutError: If request times out
            RateLimitError: If rate limit exceeded
        """
        if self.session is None or self.session.closed:
            await self.connect()

        url = self._get_url(endpoint)

        for attempt in range(self.config.max_retries + 1):
            try:
                logger.debug(f"Making {method} request to {url} (attempt {attempt + 1})")

                kwargs = {"params": params} if params else {}
                if data is not None:
                    kwargs["json"] = data

                async with self.session.request(method, url, **kwargs) as response:
                    response_data = {}

                    # Try to get JSON response
                    try:
                        response_data = await response.json()
                    except (aiohttp.ContentTypeError, ValueError):
                        # If not JSON, get text
                        response_text = await response.text()
                        if response_text:
                            response_data = {"message": response_text}

                    # Handle different status codes
                    if response.status == 200:
                        logger.debug(f"Request successful: {method} {url}")
                        return response_data

                    elif response.status == 401:
                        raise AuthenticationError(
                            response_data.get("detail", "Authentication failed")
                        )

                    elif response.status == 403:
                        # Handle job limit exceeded
                        detail = response_data.get("detail", {})
                        if isinstance(detail, dict) and "job_count" in detail:
                            raise AuthorizationError(
                                detail.get("error", "Authorization failed"),
                                plan=detail.get("plan"),
                                current_count=detail.get("job_count"),
                                max_allowed=detail.get("max_jobs"),
                            )
                        else:
                            raise AuthorizationError(
                                detail if isinstance(detail, str) else "Authorization failed"
                            )

                    elif response.status == 404:
                        raise NotFoundError("resource", endpoint.split("/")[-1])

                    elif response.status == 422:
                        # Validation error
                        detail = response_data.get("detail", "Validation error")
                        raise APIError(
                            f"Validation error: {detail}",
                            status_code=response.status,
                            response_data=response_data,
                        )

                    elif response.status == 429:
                        retry_after = response.headers.get("Retry-After")
                        raise RateLimitError(
                            "Rate limit exceeded",
                            retry_after=int(retry_after) if retry_after else None,
                        )

                    else:
                        # Generic API error
                        message = response_data.get("detail", f"HTTP {response.status}")
                        raise APIError(
                            message,
                            status_code=response.status,
                            response_data=response_data,
                        )

            except asyncio.TimeoutError:
                if attempt == self.config.max_retries:
                    raise TimeoutError(f"Request timeout after {self.config.timeout}s")
                logger.warning(f"Request timeout on attempt {attempt + 1}, retrying...")

            except (ClientConnectorError, aiohttp.ClientError) as e:
                if attempt == self.config.max_retries:
                    raise ConnectionError(f"Connection failed: {e}")
                logger.warning(f"Connection error on attempt {attempt + 1}: {e}")

            except (AuthenticationError, AuthorizationError, NotFoundError, RateLimitError):
                # Don't retry these errors
                raise

            except Exception as e:
                if attempt == self.config.max_retries:
                    raise APIError(f"Unexpected error: {e}")
                logger.warning(f"Unexpected error on attempt {attempt + 1}: {e}")

            # Wait before retrying
            if attempt < self.config.max_retries:
                delay = self.config.retry_delay * (2 ** attempt)  # Exponential backoff
                logger.debug(f"Waiting {delay}s before retry...")
                await asyncio.sleep(delay)

        # This should never be reached, but just in case
        raise APIError("Maximum retries exceeded")

    # API Methods

    async def ping(self) -> Dict[str, Any]:
        """
        Test API connectivity.

        Returns:
            Dict containing ping response
        """
        return await self._make_request("GET", "/ping")

    async def create_job(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new cron job.

        Args:
            job_data: Job configuration data

        Returns:
            Dict containing created job information
        """
        return await self._make_request("POST", "/jobs", data=job_data)

    async def list_jobs(self) -> List[Dict[str, Any]]:
        """
        List all jobs for the authenticated user.

        Returns:
            List of job dictionaries
        """
        response = await self._make_request("GET", "/jobs")
        # The API returns a list directly
        return response if isinstance(response, list) else []

    async def get_job(self, job_id: str) -> Dict[str, Any]:
        """
        Get details for a specific job.

        Args:
            job_id: ID of the job to retrieve

        Returns:
            Dict containing job information
        """
        return await self._make_request("GET", f"/jobs/{job_id}")

    async def update_job(self, job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing job.

        Args:
            job_id: ID of the job to update
            job_data: Complete job configuration data

        Returns:
            Dict containing updated job information
        """
        return await self._make_request("PUT", f"/jobs/{job_id}", data=job_data)

    async def delete_job(self, job_id: str) -> Dict[str, Any]:
        """
        Delete a job permanently.

        Args:
            job_id: ID of the job to delete

        Returns:
            Dict containing deletion confirmation
        """
        return await self._make_request("DELETE", f"/jobs/{job_id}")

    async def pause_job(self, job_id: str) -> Dict[str, Any]:
        """
        Pause a job.

        Args:
            job_id: ID of the job to pause

        Returns:
            Dict containing updated job information
        """
        return await self._make_request("POST", f"/jobs/{job_id}/pause")

    async def resume_job(self, job_id: str) -> Dict[str, Any]:
        """
        Resume a paused job.

        Args:
            job_id: ID of the job to resume

        Returns:
            Dict containing updated job information
        """
        return await self._make_request("POST", f"/jobs/{job_id}/resume")

    async def get_job_logs(self, job_id: str) -> Dict[str, Any]:
        """
        Get execution logs for a job.

        Args:
            job_id: ID of the job to get logs for

        Returns:
            Dict containing job logs information
        """
        return await self._make_request("GET", f"/jobs/{job_id}/logs")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a comprehensive health check.

        Returns:
            Dict containing health check results
        """
        try:
            start_time = asyncio.get_event_loop().time()
            ping_result = await self.ping()
            end_time = asyncio.get_event_loop().time()

            response_time = round((end_time - start_time) * 1000, 2)  # Convert to ms

            return {
                "status": "healthy",
                "api_response": ping_result,
                "response_time_ms": response_time,
                "base_url": self.config.base_url,
                "connected": True,
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "error_type": type(e).__name__,
                "base_url": self.config.base_url,
                "connected": False,
            }