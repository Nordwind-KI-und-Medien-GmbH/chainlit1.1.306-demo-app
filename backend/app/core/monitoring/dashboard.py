"""Connection monitoring dashboard and utilities."""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any
from .pg_connection_monitor import get_pg_monitor
from .connection_health_checker import get_health_checker

async def get_connection_dashboard() -> Dict[str, Any]:
    """Get a comprehensive dashboard of connection information."""
    monitor = get_pg_monitor()
    health_checker = get_health_checker()

    if not monitor:
        return {"error": "PostgreSQL monitor not initialized"}

    try:
        # Get all monitoring data
        stats = await monitor.get_connection_stats()
        long_queries = await monitor.get_long_running_queries()
        connection_details = await monitor.get_connection_details()

        # Get health checker info
        last_health_check = health_checker.get_last_stats()

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "connection_stats": stats,
            "long_running_queries": long_queries,
            "connection_details": connection_details,
            "health_checker": {
                "is_running": health_checker.is_running,
                "check_interval": health_checker.check_interval,
                "alert_thresholds": health_checker.alert_thresholds,
                "last_check": last_health_check["timestamp"].isoformat() if last_health_check else None
            },
            "recommendations": _generate_recommendations(stats, long_queries)
        }

        return dashboard

    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "status": "error"
        }

def _generate_recommendations(stats: Dict[str, Any], long_queries: list) -> list:
    """Generate optimization recommendations based on current stats."""
    recommendations = []

    db_stats = stats.get('database_stats', {})
    pool_stats = stats.get('pool_stats', {})

    # Connection usage recommendations
    usage_percent = db_stats.get('usage_percent', 0)
    if usage_percent > 80:
        recommendations.append({
            "level": "warning",
            "category": "connection_usage",
            "message": f"High database connection usage ({usage_percent:.1f}%)",
            "suggestion": "Consider optimizing queries or increasing connection limits"
        })
    elif usage_percent > 60:
        recommendations.append({
            "level": "info",
            "category": "connection_usage",
            "message": f"Moderate database connection usage ({usage_percent:.1f}%)",
            "suggestion": "Monitor connection patterns and consider connection pooling optimization"
        })

    # Pool recommendations
    pool_size = pool_stats.get('pool_size', 1)
    checked_out = pool_stats.get('checked_out', 0)
    overflow = pool_stats.get('overflow', 0)

    if overflow > 0:
        recommendations.append({
            "level": "warning",
            "category": "connection_pool",
            "message": f"Connection pool overflow detected ({overflow} overflow connections)",
            "suggestion": "Consider increasing pool_size or max_overflow parameters"
        })

    pool_usage = (checked_out / pool_size * 100) if pool_size > 0 else 0
    if pool_usage > 80:
        recommendations.append({
            "level": "warning",
            "category": "connection_pool",
            "message": f"High pool usage ({pool_usage:.1f}%)",
            "suggestion": "Consider increasing pool size or optimizing connection lifecycle"
        })

    # Long query recommendations
    if len(long_queries) > 5:
        recommendations.append({
            "level": "warning",
            "category": "query_performance",
            "message": f"Multiple long-running queries detected ({len(long_queries)})",
            "suggestion": "Review and optimize slow queries to free up connections"
        })
    elif len(long_queries) > 0:
        recommendations.append({
            "level": "info",
            "category": "query_performance",
            "message": f"Long-running queries detected ({len(long_queries)})",
            "suggestion": "Monitor query performance and consider optimization"
        })

    return recommendations

async def print_connection_summary():
    """Print a formatted connection summary to console."""
    dashboard = await get_connection_dashboard()

    if "error" in dashboard:
        print(f"❌ Error getting connection stats: {dashboard['error']}")
        return

    stats = dashboard.get('connection_stats', {})
    db_stats = stats.get('database_stats', {})
    pool_stats = stats.get('pool_stats', {})
    long_queries = dashboard.get('long_running_queries', [])
    recommendations = dashboard.get('recommendations', [])

    print("\n" + "="*60)
    print("📊 POSTGRESQL CONNECTION DASHBOARD")
    print("="*60)
    print(f"🕐 Timestamp: {dashboard.get('timestamp', 'N/A')}")
    print(f"📊 Status: {stats.get('status', 'unknown').upper()}")

    print("\n🔌 DATABASE CONNECTIONS:")
    print(f"   Active: {db_stats.get('active_connections', 'N/A')}/{db_stats.get('max_connections', 'N/A')}")
    print(f"   Usage: {db_stats.get('usage_percent', 0):.1f}%")

    print("\n🏊 CONNECTION POOL:")
    print(f"   Pool Size: {pool_stats.get('pool_size', 'N/A')}")
    print(f"   Checked Out: {pool_stats.get('checked_out', 'N/A')}")
    print(f"   Overflow: {pool_stats.get('overflow', 'N/A')}")
    print(f"   Invalid: {pool_stats.get('invalid', 'N/A')}")

    print(f"\n⏱️  LONG-RUNNING QUERIES: {len(long_queries)}")
    for i, query in enumerate(long_queries[:3]):
        print(f"   Query {i+1}: {query['duration']} (PID: {query['pid']})")

    print(f"\n💡 RECOMMENDATIONS: {len(recommendations)}")
    for rec in recommendations:
        emoji = "⚠️" if rec['level'] == 'warning' else "ℹ️"
        print(f"   {emoji} {rec['message']}")
        print(f"      → {rec['suggestion']}")

    print("="*60 + "\n")

def save_dashboard_to_file(filepath: str = "connection_dashboard.json"):
    """Save current dashboard to a JSON file."""
    async def _save():
        dashboard = await get_connection_dashboard()
        with open(filepath, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        print(f"📄 Dashboard saved to {filepath}")

    asyncio.run(_save())

async def monitor_connections_live(interval: int = 30, duration: int = 300):
    """Monitor connections live for a specified duration."""
    print(f"🔄 Starting live monitoring for {duration} seconds (interval: {interval}s)")

    end_time = datetime.now().timestamp() + duration
    while datetime.now().timestamp() < end_time:
        await print_connection_summary()
        await asyncio.sleep(interval)

    print("✅ Live monitoring completed")
