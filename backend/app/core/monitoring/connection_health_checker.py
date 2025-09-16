"""Connection Health Checker for monitoring database connections over time."""

import asyncio
import logging
from datetime import datetime
from typing import Optional
from .pg_connection_monitor import get_pg_monitor

logger = logging.getLogger(__name__)


class ConnectionHealthChecker:
    """Periodic health checker for database connections."""

    def __init__(self, check_interval: int = 300):  # 5 minutes default
        """Initialize the health checker.

        Args:
            check_interval: Interval in seconds between health checks
        """
        self.check_interval = check_interval
        self.is_running = False
        self._task: Optional[asyncio.Task] = None
        self.last_stats = None
        self.alert_thresholds = {
            "connection_usage_percent": 80,
            "long_running_query_minutes": 10,
            "pool_exhaustion_percent": 90
        }

    async def start_monitoring(self):
        """Start periodic connection health monitoring."""
        if self.is_running:
            logger.warning("Health checker is already running")
            return

        self.is_running = True
        # Don't await the task to prevent blocking
        self._task = asyncio.create_task(self._monitoring_loop())
        logger.info(f"Started connection health monitoring with {self.check_interval}s interval")

    async def stop_monitoring(self):
        """Stop the monitoring loop."""
        self.is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Stopped connection health monitoring")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_running:
            try:
                await self._perform_health_check()
            except Exception as e:
                logger.error(f"Health check error: {e}")

            try:
                await asyncio.sleep(self.check_interval)
            except asyncio.CancelledError:
                break

    async def _perform_health_check(self):
        """Perform a single health check."""
        monitor = get_pg_monitor()
        if not monitor:
            logger.warning("PostgreSQL monitor not initialized")
            return

        try:
            # Get current stats
            stats = await monitor.get_connection_stats()
            long_queries = await monitor.get_long_running_queries()
            connection_details = await monitor.get_connection_details()

            # Store current stats
            self.last_stats = {
                "timestamp": datetime.now(),
                "stats": stats,
                "long_queries": long_queries,
                "connection_details": connection_details
            }

            # Log current status
            await self._log_status(stats, long_queries, connection_details)

            # Check for alerts
            await self._check_alerts(stats, long_queries)

        except Exception as e:
            logger.error(f"Error during health check: {e}")

    async def _log_status(self, stats, long_queries, connection_details):
        """Log current connection status."""
        db_stats = stats.get('database_stats', {})
        pool_stats = stats.get('pool_stats', {})

        status_msg = f"""
=== PostgreSQL Health Check ===
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database Connections: {db_stats.get('active_connections', 'N/A')}/{db_stats.get('max_connections', 'N/A')}
Connection Usage: {db_stats.get('usage_percent', 0):.1f}%
Pool Status: {pool_stats.get('checked_out', 0)}/{pool_stats.get('pool_size', 0)} checked out
Pool Overflow: {pool_stats.get('overflow', 0)}
Long Running Queries: {len(long_queries)}
Status: {stats.get('status', 'unknown')}
"""

        if stats.get('status') == 'healthy':
            logger.info(status_msg)
        else:
            logger.warning(status_msg)

    async def _check_alerts(self, stats, long_queries):
        """Check for alert conditions and log warnings."""
        db_stats = stats.get('database_stats', {})
        pool_stats = stats.get('pool_stats', {})

        # Check connection usage
        usage_percent = db_stats.get('usage_percent', 0)
        if usage_percent > self.alert_thresholds['connection_usage_percent']:
            logger.warning(f"ALERT: Database connection usage is {usage_percent:.1f}% (threshold: {self.alert_thresholds['connection_usage_percent']}%)")

        # Check pool exhaustion
        pool_size = pool_stats.get('pool_size', 1)
        checked_out = pool_stats.get('checked_out', 0)
        pool_usage = (checked_out / pool_size * 100) if pool_size > 0 else 0

        if pool_usage > self.alert_thresholds['pool_exhaustion_percent']:
            logger.warning(f"ALERT: Connection pool usage is {pool_usage:.1f}% (threshold: {self.alert_thresholds['pool_exhaustion_percent']}%)")

        # Check long-running queries
        if long_queries:
            logger.warning(f"ALERT: Found {len(long_queries)} long-running queries:")
            for i, query in enumerate(long_queries[:3]):  # Log first 3
                logger.warning(f"  Query {i+1} (PID {query['pid']}): Running for {query['duration']}")
                logger.warning(f"    SQL: {query['query'][:100]}...")

    def get_last_stats(self):
        """Get the last collected statistics."""
        return self.last_stats

    async def force_health_check(self):
        """Force an immediate health check."""
        await self._perform_health_check()
        return self.last_stats

    def update_thresholds(self, **thresholds):
        """Update alert thresholds.

        Args:
            connection_usage_percent: Alert when connection usage exceeds this percent
            long_running_query_minutes: Alert when queries run longer than this
            pool_exhaustion_percent: Alert when pool usage exceeds this percent
        """
        for key, value in thresholds.items():
            if key in self.alert_thresholds:
                self.alert_thresholds[key] = value
                logger.info(f"Updated alert threshold {key} to {value}")


# Global health checker instance
health_checker = ConnectionHealthChecker()


async def start_health_monitoring(check_interval: int = 300):
    """Start health monitoring with specified interval."""
    health_checker.check_interval = check_interval
    await health_checker.start_monitoring()


async def stop_health_monitoring():
    """Stop health monitoring."""
    await health_checker.stop_monitoring()


def get_health_checker() -> ConnectionHealthChecker:
    """Get the global health checker instance."""
    return health_checker
