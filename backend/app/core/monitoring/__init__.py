"""Monitoring infrastructure for the application."""

from .pg_connection_monitor import PostgreSQLConnectionMonitor, pg_monitor, initialize_pg_monitor, get_pg_monitor
from .connection_health_checker import ConnectionHealthChecker, health_checker, start_health_monitoring, stop_health_monitoring, get_health_checker
from .dashboard import get_connection_dashboard, print_connection_summary, save_dashboard_to_file, monitor_connections_live

# Import register_phoenix_tracer module (it registers itself on import)
from . import register_phoenix_tracer

__all__ = [
    'PostgreSQLConnectionMonitor',
    'pg_monitor',
    'initialize_pg_monitor',
    'get_pg_monitor',
    'ConnectionHealthChecker',
    'health_checker',
    'start_health_monitoring',
    'stop_health_monitoring',
    'get_health_checker',
    'get_connection_dashboard',
    'print_connection_summary',
    'save_dashboard_to_file',
    'monitor_connections_live',
    'register_phoenix_tracer'
]
