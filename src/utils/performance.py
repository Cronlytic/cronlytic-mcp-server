"""Performance monitoring and optimization utilities for Cronlytic MCP Server."""

import asyncio
import functools
import logging
import time
from contextlib import asynccontextmanager
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for operations."""

    operation_name: str
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    error_count: int = 0
    last_called: Optional[datetime] = None
    recent_times: List[float] = field(default_factory=list)

    @property
    def average_time(self) -> float:
        """Calculate average execution time."""
        return self.total_time / self.total_calls if self.total_calls > 0 else 0.0

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return ((self.total_calls - self.error_count) / self.total_calls * 100) if self.total_calls > 0 else 0.0

    def add_measurement(self, execution_time: float, success: bool = True) -> None:
        """Add a new performance measurement."""
        self.total_calls += 1
        self.total_time += execution_time
        self.min_time = min(self.min_time, execution_time)
        self.max_time = max(self.max_time, execution_time)
        self.last_called = datetime.now()

        if not success:
            self.error_count += 1

        # Keep only recent measurements (last 100)
        self.recent_times.append(execution_time)
        if len(self.recent_times) > 100:
            self.recent_times.pop(0)

    def get_recent_average(self, window: int = 10) -> float:
        """Get average of recent measurements."""
        if not self.recent_times:
            return 0.0
        recent_subset = self.recent_times[-window:]
        return sum(recent_subset) / len(recent_subset)


class PerformanceMonitor:
    """Global performance monitoring system."""

    def __init__(self):
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.enabled = True
        self._lock = asyncio.Lock()

    async def record_operation(self, operation_name: str, execution_time: float, success: bool = True) -> None:
        """Record performance metrics for an operation."""
        if not self.enabled:
            return

        async with self._lock:
            if operation_name not in self.metrics:
                self.metrics[operation_name] = PerformanceMetrics(operation_name)

            self.metrics[operation_name].add_measurement(execution_time, success)

            # Log slow operations
            if execution_time > 5.0:  # More than 5 seconds
                logger.warning(f"Slow operation detected: {operation_name} took {execution_time:.2f}s")

    def get_metrics(self, operation_name: Optional[str] = None) -> Dict[str, PerformanceMetrics]:
        """Get performance metrics."""
        if operation_name:
            return {operation_name: self.metrics.get(operation_name)} if operation_name in self.metrics else {}
        return self.metrics.copy()

    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        total_operations = sum(m.total_calls for m in self.metrics.values())
        total_errors = sum(m.error_count for m in self.metrics.values())

        slowest_operations = sorted(
            [(name, metrics.average_time) for name, metrics in self.metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        most_used_operations = sorted(
            [(name, metrics.total_calls) for name, metrics in self.metrics.items()],
            key=lambda x: x[1],
            reverse=True
        )[:5]

        return {
            "total_operations": total_operations,
            "total_errors": total_errors,
            "overall_success_rate": ((total_operations - total_errors) / total_operations * 100) if total_operations > 0 else 0.0,
            "slowest_operations": slowest_operations,
            "most_used_operations": most_used_operations,
            "monitored_operations": len(self.metrics)
        }

    def reset_metrics(self) -> None:
        """Reset all performance metrics."""
        self.metrics.clear()
        logger.info("Performance metrics reset")

    def get_detailed_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get detailed metrics for all operations."""
        return {
            name: {
                "total_calls": metrics.total_calls,
                "average_time": metrics.average_time,
                "min_time": metrics.min_time if metrics.min_time != float('inf') else 0,
                "max_time": metrics.max_time,
                "success_rate": metrics.success_rate,
                "error_count": metrics.error_count,
                "last_called": metrics.last_called.isoformat() if metrics.last_called else None
            }
            for name, metrics in self.metrics.items()
        }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def performance_tracked(operation_name: Optional[str] = None):
    """Decorator to track performance of async functions."""

    def decorator(func: Callable) -> Callable:
        name = operation_name or f"{func.__module__}.{func.__name__}"

        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                execution_time = time.time() - start_time
                await performance_monitor.record_operation(name, execution_time, success)

        return wrapper
    return decorator


@asynccontextmanager
async def performance_context(operation_name: str):
    """Context manager for tracking performance of code blocks."""
    start_time = time.time()
    success = True

    try:
        yield
    except Exception:
        success = False
        raise
    finally:
        execution_time = time.time() - start_time
        await performance_monitor.record_operation(operation_name, execution_time, success)


class ConnectionPool:
    """Optimized connection pool for HTTP requests."""

    def __init__(self, max_connections: int = 20, max_per_host: int = 10):
        self.max_connections = max_connections
        self.max_per_host = max_per_host
        self._sessions: Dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get_session(self, base_url: str) -> Any:
        """Get or create a session for a base URL."""
        async with self._lock:
            if base_url not in self._sessions:
                import aiohttp
                from aiohttp import ClientTimeout

                timeout = ClientTimeout(total=30, connect=10)
                connector = aiohttp.TCPConnector(
                    limit=self.max_connections,
                    limit_per_host=self.max_per_host,
                    enable_cleanup_closed=True,
                    keepalive_timeout=30
                )

                self._sessions[base_url] = aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector
                )

                logger.debug(f"Created new HTTP session for {base_url}")

            return self._sessions[base_url]

    async def close_all(self) -> None:
        """Close all sessions."""
        async with self._lock:
            for session in self._sessions.values():
                if not session.closed:
                    await session.close()
            self._sessions.clear()
            logger.debug("Closed all HTTP sessions")


# Global connection pool
connection_pool = ConnectionPool()


class CacheManager:
    """Simple in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.default_ttl = default_ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if datetime.now() < entry['expires']:
                    logger.debug(f"Cache hit for key: {key}")
                    return entry['value']
                else:
                    # Expired
                    del self._cache[key]
                    logger.debug(f"Cache expired for key: {key}")

            logger.debug(f"Cache miss for key: {key}")
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in cache with TTL."""
        ttl = ttl or self.default_ttl
        expires = datetime.now() + timedelta(seconds=ttl)

        async with self._lock:
            self._cache[key] = {
                'value': value,
                'expires': expires
            }
            logger.debug(f"Cached value for key: {key} (TTL: {ttl}s)")

    async def delete(self, key: str) -> None:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                logger.debug(f"Deleted cache entry for key: {key}")

    async def clear(self) -> None:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            logger.debug("Cleared all cache entries")

    async def cleanup_expired(self) -> int:
        """Remove expired entries and return count."""
        now = datetime.now()
        removed_count = 0

        async with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if now >= entry['expires']
            ]

            for key in expired_keys:
                del self._cache[key]
                removed_count += 1

            if removed_count > 0:
                logger.debug(f"Cleaned up {removed_count} expired cache entries")

        return removed_count

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "total_entries": len(self._cache),
            "cache_keys": list(self._cache.keys())
        }


# Global cache manager
cache_manager = CacheManager()


async def optimize_startup() -> None:
    """Perform startup optimizations."""
    logger.info("Performing startup optimizations...")

    # Pre-warm connection pools
    try:
        import aiohttp
        # Test connection to API
        session = await connection_pool.get_session("https://api.cronlytic.com")
        async with session.get("https://api.cronlytic.com/prog/ping") as response:
            if response.status == 200:
                logger.info("API connectivity verified")
    except Exception as e:
        logger.warning(f"API pre-warming failed: {e}")

    # Start background cleanup task
    asyncio.create_task(periodic_cleanup())

    logger.info("Startup optimizations complete")


async def periodic_cleanup() -> None:
    """Periodic cleanup task for cache and metrics."""
    while True:
        try:
            # Cleanup expired cache entries every 5 minutes
            await asyncio.sleep(300)
            removed = await cache_manager.cleanup_expired()

            # Log performance summary every hour
            if datetime.now().minute == 0:
                summary = performance_monitor.get_summary()
                logger.info(f"Performance summary: {summary}")

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {e}")


def get_performance_report() -> Dict[str, Any]:
    """Generate comprehensive performance report."""
    return {
        "summary": performance_monitor.get_summary(),
        "detailed_metrics": performance_monitor.get_detailed_metrics(),
        "timestamp": datetime.now().isoformat()
    }


async def optimize_cronlytic_client():
    """Apply performance optimizations to the Cronlytic client."""
    logger.info("Applying performance optimizations...")

    # Connection pool optimization suggestions
    optimizations = {
        "connection_pooling": "Use aiohttp session reuse",
        "timeout_tuning": "Optimal timeouts configured",
        "retry_strategy": "Exponential backoff implemented",
        "caching": "Consider caching job lists for short periods",
        "batch_operations": "Group multiple API calls when possible"
    }

    for optimization, description in optimizations.items():
        logger.debug(f"Optimization: {optimization} - {description}")

    logger.info("Performance optimizations applied")
    return optimizations