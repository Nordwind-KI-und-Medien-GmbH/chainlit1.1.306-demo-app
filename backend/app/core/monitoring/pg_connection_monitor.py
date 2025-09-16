"""PostgreSQL Connection Monitor for Azure PostgreSQL database."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy import text
from datetime import datetime

logger = logging.getLogger(__name__)


class PostgreSQLConnectionMonitor:
    """Monitor PostgreSQL connections for Azure PostgreSQL database."""

    def __init__(self, database_url: str):
        """Initialize the connection monitor with database URL."""
        self.database_url = database_url
        self.engine: Optional[AsyncEngine] = None
        self._lock = asyncio.Lock()  # Prevent concurrent operations
        self._create_engine()

    def _create_engine(self):
        """Create SQLAlchemy async engine for monitoring."""
        try:
            # Convert database URL to async if needed
            if not self.database_url.startswith(('postgresql+asyncpg://', 'postgresql+psycopg://')):
                # Convert sync URL to async URL
                if self.database_url.startswith('postgresql://'):
                    async_url = self.database_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
                else:
                    async_url = self.database_url
            else:
                async_url = self.database_url

            # Create async engine for monitoring with separate connection pool
            self.engine = create_async_engine(
                async_url,
                echo=False,
                pool_size=2,  # Small pool for monitoring only
                max_overflow=1,
                pool_pre_ping=True,
                pool_recycle=300,  # Shorter recycle time for monitoring
            )
            logger.info("PostgreSQL connection monitor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL engine: {e}")
            self.engine = None

    async def get_connection_stats(self) -> Dict[str, Any]:
        """Get current PostgreSQL connection statistics."""
        if not self.engine:
            return {"error": "Engine not initialized"}

        async with self._lock:  # Prevent concurrent operations
            try:
                async with self.engine.connect() as conn:
                    # Get active connections to your database
                    result = await conn.execute(text("""
                        SELECT
                            count(*) as active_connections,
                            (SELECT setting FROM pg_settings WHERE name = 'max_connections') as max_connections
                        FROM pg_stat_activity psa
                        WHERE psa.datname = current_database()
                        AND psa.state = 'active'
                    """))

                    stats = result.fetchone()

                    # Calculate usage percentage
                    active_connections = int(stats[0]) if stats else 0
                    max_connections = int(stats[1]) if stats else 0
                    usage_percent = (active_connections / max_connections * 100) if max_connections > 0 else 0

                    # Get pool statistics (basic info only since we're not using QueuePool)
                    pool_stats = {
                        "pool_type": str(type(self.engine.pool).__name__),
                        "pool_size": getattr(self.engine.pool, 'size', lambda: 'N/A')(),
                        "checked_in": getattr(self.engine.pool, 'checkedin', lambda: 'N/A')(),
                        "checked_out": getattr(self.engine.pool, 'checkedout', lambda: 'N/A')(),
                        "overflow": getattr(self.engine.pool, 'overflow', lambda: 0)(),
                        "invalid": getattr(self.engine.pool, 'invalid', lambda: 0)(),
                    }

                    return {
                        "timestamp": datetime.now().isoformat(),
                        "database_stats": {
                            "active_connections": active_connections,
                            "max_connections": max_connections,
                            "usage_percent": usage_percent
                        },
                        "pool_stats": pool_stats,
                        "status": "healthy"
                    }
            except Exception as e:
                logger.error(f"Error getting connection stats: {e}")
                return {
                    "timestamp": datetime.now().isoformat(),
                    "error": str(e),
                    "status": "error"
                }

    async def get_long_running_queries(self) -> List[Dict[str, Any]]:
        """Identify long-running queries that might be holding connections."""
        if not self.engine:
            return []

        async with self._lock:  # Prevent concurrent operations
            try:
                async with self.engine.connect() as conn:
                    result = await conn.execute(text("""
                        SELECT
                            pid,
                            now() - pg_stat_activity.query_start AS duration,
                            query,
                            state,
                            application_name,
                            client_addr,
                            usename
                        FROM pg_stat_activity
                        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
                        AND state = 'active'
                        AND datname = current_database()
                        ORDER BY duration DESC
                        LIMIT 10
                    """))

                    queries = []
                    for row in result:
                        queries.append({
                            "pid": row[0],
                            "duration": str(row[1]),
                            "query": row[2][:200] + "..." if len(row[2]) > 200 else row[2],  # Truncate long queries
                            "state": row[3],
                            "application_name": row[4],
                            "client_addr": str(row[5]) if row[5] else None,
                            "username": row[6]
                        })

                    return queries

            except Exception as e:
                logger.error(f"Error getting long-running queries: {e}")
                return []

    async def get_connection_details(self) -> Dict[str, Any]:
        """Get detailed connection information."""
        if not self.engine:
            return {"error": "Engine not initialized"}

        try:
            async with self.engine.connect() as conn:
                # Get all connections to current database
                result = await conn.execute(text("""
                    SELECT
                        state,
                        count(*) as count,
                        application_name
                    FROM pg_stat_activity
                    WHERE datname = current_database()
                    GROUP BY state, application_name
                    ORDER BY count DESC
                """))

                connections_by_state = []
                for row in result:
                    connections_by_state.append({
                        "state": row[0],
                        "count": int(row[1]),
                        "application_name": row[2]
                    })

                return {
                    "timestamp": datetime.now().isoformat(),
                    "connections_by_state": connections_by_state,
                    "status": "healthy"
                }

        except Exception as e:
            logger.error(f"Error getting connection details: {e}")
            return {
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "status": "error"
            }

    def get_engine(self) -> Optional[AsyncEngine]:
        """Get the SQLAlchemy async engine for use by data layer."""
        return self.engine

    async def test_connection(self) -> bool:
        """Test if database connection is working."""
        if not self.engine:
            return False

        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False


# Global monitor instance - will be initialized when data layer is set up
pg_monitor: Optional[PostgreSQLConnectionMonitor] = None


def initialize_pg_monitor(database_url: str) -> PostgreSQLConnectionMonitor:
    """Initialize the global PostgreSQL monitor."""
    global pg_monitor
    pg_monitor = PostgreSQLConnectionMonitor(database_url)
    return pg_monitor


def get_pg_monitor() -> Optional[PostgreSQLConnectionMonitor]:
    """Get the global PostgreSQL monitor instance."""
    return pg_monitor
