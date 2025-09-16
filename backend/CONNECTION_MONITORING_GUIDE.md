# PostgreSQL Connection Optimization Guide

## Overview

This application now includes comprehensive PostgreSQL connection monitoring for your Azure PostgreSQL instance. This guide explains how to use the monitoring tools and optimize connection usage.

## 🔧 Configuration Options

### Environment Variables

Add these to your `.env` file for connection optimization:

```bash
# PostgreSQL Connection Pool Settings (add to DATABASE_URL parameters)
DATABASE_URL="postgresql://user:password@host:port/database?options=-c%20timezone%3Dutc&connect_timeout=10&command_timeout=30"

# Optional: Health monitoring interval (seconds)
PG_MONITOR_INTERVAL=300  # 5 minutes

# Optional: Alert thresholds
PG_CONNECTION_USAGE_ALERT=80  # Percent
PG_POOL_USAGE_ALERT=90        # Percent
```

### Connection Pool Parameters

The monitoring system uses these optimized defaults:

```python
# Connection Pool Settings (configured in pg_connection_monitor.py)
pool_size=5                # Base connections in pool
max_overflow=10            # Additional connections when needed
pool_pre_ping=True         # Validate connections before use
pool_recycle=3600          # Recycle connections every hour
pool_timeout=30            # Timeout when getting connection from pool
```

## 📊 Monitoring Tools

### 1. CLI Monitoring Tool

```bash
# Basic status
python backend/monitor_cli.py status

# Full dashboard
python backend/monitor_cli.py dashboard

# Live monitoring (30s intervals, 5 minutes total)
python backend/monitor_cli.py live --interval 30 --duration 300

# Save dashboard to file
python backend/monitor_cli.py save connection_report.json
```

### 2. Programmatic Monitoring

```python
from app.core.monitoring import get_connection_dashboard, print_connection_summary

# Get dashboard data
dashboard = await get_connection_dashboard()

# Print formatted summary
await print_connection_summary()
```

### 3. Automatic Health Monitoring

The system automatically starts health monitoring when a chat session begins:

- ✅ Monitors every 5 minutes by default
- ✅ Alerts on high connection usage (>80%)
- ✅ Tracks long-running queries (>5 minutes)
- ✅ Logs pool exhaustion warnings

## 🎯 Connection Optimization Strategies

### 1. **Monitor Connection Usage Patterns**

```bash
# Run this during peak usage to identify patterns
python backend/monitor_cli.py live --interval 15 --duration 600
```

**What to look for:**
- Connection usage spikes during certain operations
- Pool overflow during concurrent chat sessions
- Long-running queries that hold connections

### 2. **Adjust Pool Settings Based on Usage**

Edit `backend/app/core/monitoring/pg_connection_monitor.py`:

```python
# For high-traffic applications
pool_size=10               # Increase base pool
max_overflow=20            # Allow more overflow

# For low-traffic applications  
pool_size=3                # Reduce base pool
max_overflow=5             # Limit overflow
```

### 3. **Azure PostgreSQL Tier Optimization**

| Azure Tier | Max Connections | Recommended Pool Settings |
|------------|----------------|--------------------------|
| Basic      | 50-100         | pool_size=3, max_overflow=5 |
| General Purpose | 100-1000  | pool_size=5, max_overflow=10 |
| Memory Optimized | 1000+    | pool_size=10, max_overflow=20 |

### 4. **Connection Lifecycle Optimization**

**For RAG operations:**
- Use connection pooling for vector searches
- Close connections promptly after document processing
- Batch similar operations

**For Chat sessions:**
- Monitor memory usage vs connection retention
- Implement connection cleanup on session end
- Use async operations where possible

## 🚨 Alert Thresholds and Actions

### High Connection Usage (>80%)

**Immediate Actions:**
1. Check for long-running queries: `python backend/monitor_cli.py dashboard`
2. Identify concurrent users/sessions
3. Consider upgrading Azure PostgreSQL tier

**Long-term Solutions:**
- Implement connection pooling optimizations
- Review query performance
- Add connection cleanup procedures

### Pool Exhaustion (>90%)

**Immediate Actions:**
1. Increase `max_overflow` temporarily
2. Restart application to reset pool
3. Monitor for connection leaks

**Long-term Solutions:**
- Increase `pool_size`
- Implement better connection lifecycle management
- Add connection monitoring alerts

### Long-running Queries

**Investigation:**
```bash
# Check for long-running queries
python backend/monitor_cli.py dashboard
```

**Common Causes:**
- Complex RAG similarity searches
- Large document processing
- Unoptimized database queries

## 📈 Performance Monitoring

### Key Metrics to Track

1. **Connection Usage Percent**
   - Target: <60% normal, <80% peak
   - Alert: >80%

2. **Pool Utilization**
   - Target: <70% normal, <90% peak
   - Alert: >90%

3. **Long-running Queries**
   - Target: <5 queries >5 minutes
   - Alert: >10 queries >5 minutes

4. **Connection Lifecycle**
   - Target: Connections released <30 seconds
   - Alert: Connections held >5 minutes

### Dashboard Interpretation

```json
{
  "database_stats": {
    "active_connections": 15,      // Current DB connections
    "max_connections": 100,        // Azure PostgreSQL limit
    "usage_percent": 15.0          // 15% usage - healthy
  },
  "pool_stats": {
    "pool_size": 5,               // Base pool size
    "checked_out": 2,             // Currently in use
    "overflow": 0,                // Extra connections created
    "invalid": 0                  // Broken connections
  }
}
```

## 🔄 Automated Optimization

### Connection Pool Auto-scaling

```python
# Add to your config for dynamic scaling
def get_optimal_pool_size():
    """Calculate optimal pool size based on usage patterns."""
    avg_concurrent_sessions = get_avg_concurrent_sessions()
    return max(3, min(20, avg_concurrent_sessions * 2))
```

### Health-based Alerts

```python
# Configure alerts in your monitoring
health_checker.update_thresholds(
    connection_usage_percent=75,  # Lower threshold for early warning
    pool_exhaustion_percent=85,   # Alert before complete exhaustion
)
```

## 🛠️ Troubleshooting

### Connection Leaks

**Symptoms:**
- Gradually increasing connection count
- Pool exhaustion during normal load
- Application slowdown over time

**Diagnosis:**
```bash
python backend/monitor_cli.py live --interval 10 --duration 180
```

**Solutions:**
1. Review RAG operation cleanup
2. Check async operation completion
3. Add explicit connection cleanup in exception handlers

### High Latency

**Symptoms:**
- Slow response times
- Connection timeouts
- Pool wait times

**Solutions:**
1. Increase `pool_timeout`
2. Add connection validation (`pool_pre_ping=True`)
3. Optimize query performance

### Azure PostgreSQL Limits

**Check your Azure PostgreSQL limits:**
1. Connection limits based on tier
2. Network bandwidth limitations
3. Regional latency considerations

## 📋 Maintenance Checklist

### Daily
- [ ] Check connection usage trends
- [ ] Review long-running query alerts
- [ ] Monitor pool overflow events

### Weekly
- [ ] Analyze peak usage patterns
- [ ] Review connection lifecycle metrics
- [ ] Update pool settings if needed

### Monthly
- [ ] Review Azure PostgreSQL tier requirements
- [ ] Analyze connection optimization opportunities
- [ ] Update monitoring thresholds based on growth

## 🎯 Best Practices Summary

1. **Start monitoring immediately** - Use CLI tools during development
2. **Set appropriate thresholds** - Based on your Azure tier and usage
3. **Monitor during peak loads** - Identify scaling requirements early
4. **Regular maintenance** - Clean up connections, optimize queries
5. **Plan for growth** - Monitor trends and scale proactively

For more detailed monitoring, check the logs and use the dashboard tools provided!
