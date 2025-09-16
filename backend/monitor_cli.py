#!/usr/bin/env python3
"""
PostgreSQL Connection Monitoring CLI Tool

This script provides command-line tools for monitoring PostgreSQL connections
in your Chainlit application.

Usage examples:
    poetry run python monitor_cli.py status           # Show current connection status
    poetry run python monitor_cli.py dashboard        # Show full dashboard
    poetry run python monitor_cli.py live --interval 30 --duration 300  # Live monitoring
    poetry run python monitor_cli.py save dashboard.json  # Save dashboard to file
"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from app.core.config import simple_rag_config
from app.core.monitoring import (
    initialize_pg_monitor,
    get_connection_dashboard,
    print_connection_summary,
    save_dashboard_to_file,
    monitor_connections_live
)

async def show_status():
    """Show basic connection status."""
    # Initialize monitor
    monitor = initialize_pg_monitor(simple_rag_config.DATABASE_URL)

    # Test connection
    connection_ok = await monitor.test_connection()
    if not connection_ok:
        print("❌ Database connection failed!")
        return

    # Get basic stats
    stats = await monitor.get_connection_stats()
    db_stats = stats.get('database_stats', {})
    pool_stats = stats.get('pool_stats', {})

    print("📊 PostgreSQL Connection Status")
    print("-" * 40)
    print(f"Status: {'✅ Healthy' if stats.get('status') == 'healthy' else '❌ Error'}")
    print(f"Active Connections: {db_stats.get('active_connections', 'N/A')}/{db_stats.get('max_connections', 'N/A')}")
    print(f"Usage: {db_stats.get('usage_percent', 0):.1f}%")
    print(f"Pool Checked Out: {pool_stats.get('checked_out', 'N/A')}/{pool_stats.get('pool_size', 'N/A')}")

async def show_dashboard():
    """Show full connection dashboard."""
    # Initialize monitor
    initialize_pg_monitor(simple_rag_config.DATABASE_URL)

    # Print dashboard
    await print_connection_summary()

async def live_monitoring(interval: int, duration: int):
    """Start live monitoring."""
    # Initialize monitor
    initialize_pg_monitor(simple_rag_config.DATABASE_URL)

    # Start live monitoring
    await monitor_connections_live(interval=interval, duration=duration)

async def save_dashboard(filepath: str):
    """Save dashboard to file."""
    # Initialize monitor
    initialize_pg_monitor(simple_rag_config.DATABASE_URL)

    # Save dashboard
    save_dashboard_to_file(filepath)

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="PostgreSQL Connection Monitor")

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Status command
    subparsers.add_parser('status', help='Show current connection status')

    # Dashboard command
    subparsers.add_parser('dashboard', help='Show full connection dashboard')

    # Live monitoring command
    live_parser = subparsers.add_parser('live', help='Start live monitoring')
    live_parser.add_argument('--interval', '-i', type=int, default=30,
                            help='Monitoring interval in seconds (default: 30)')
    live_parser.add_argument('--duration', '-d', type=int, default=300,
                            help='Monitoring duration in seconds (default: 300)')

    # Save command
    save_parser = subparsers.add_parser('save', help='Save dashboard to file')
    save_parser.add_argument('filepath', nargs='?', default='dashboard.json',
                            help='Output file path (default: dashboard.json)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Run the appropriate command
    try:
        if args.command == 'status':
            asyncio.run(show_status())
        elif args.command == 'dashboard':
            asyncio.run(show_dashboard())
        elif args.command == 'live':
            asyncio.run(live_monitoring(args.interval, args.duration))
        elif args.command == 'save':
            asyncio.run(save_dashboard(args.filepath))
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped by user")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
