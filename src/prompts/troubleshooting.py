"""Troubleshooting and optimization prompts for the Cronlytic MCP Server."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class TroubleshootingPrompts:
    """Interactive prompts for troubleshooting and system optimization."""

    @staticmethod
    def get_prompts() -> List[Dict[str, Any]]:
        """Get all troubleshooting prompts."""
        return [
            SYSTEM_DIAGNOSTICS_PROMPT,
            ERROR_ANALYSIS_PROMPT,
            PERFORMANCE_OPTIMIZATION_PROMPT,
            MAINTENANCE_GUIDE_PROMPT,
        ]


# System Diagnostics Prompt
SYSTEM_DIAGNOSTICS_PROMPT = {
    "name": "system_diagnostics",
    "description": "Comprehensive system health check and diagnostics guide",
    "arguments": [
        {
            "name": "diagnostic_level",
            "description": "Level of diagnostics: quick, standard, or comprehensive",
            "required": False
        },
        {
            "name": "focus_area",
            "description": "Specific area to focus diagnostics on",
            "required": False
        }
    ],
    "template": """# System Diagnostics & Health Check

I'll perform comprehensive diagnostics to assess your Cronlytic MCP server health and identify any issues.

## 🔍 Diagnostic Overview

**Diagnostic Level:** {diagnostic_level}
**Focus Area:** {focus_area}

### Available Diagnostic Levels

**🚀 Quick Check (2-3 minutes)**
- Basic connectivity test
- Authentication validation
- Recent job status
- Critical error detection

**🔧 Standard Diagnostics (5-10 minutes)**
- Comprehensive health check
- Job performance analysis
- Configuration validation
- Error pattern analysis

**🔬 Comprehensive Analysis (15-30 minutes)**
- Deep system analysis
- Historical performance trends
- Optimization recommendations
- Preventive maintenance suggestions

## 📊 Quick Health Dashboard

### System Status
- ✅ **API Connectivity**: Test connection to Cronlytic API
- ✅ **Authentication**: Verify credentials are valid
- ✅ **MCP Integration**: Check Claude Desktop connection
- ✅ **Job Health**: Overall job success rates

### Critical Metrics
- **Total Jobs**: Count of all configured jobs
- **Active Jobs**: Currently enabled and scheduled
- **Success Rate**: Last 24 hours execution success
- **Error Count**: Recent failures requiring attention

## 🛠️ Diagnostic Categories

### 1. **Connectivity Diagnostics**
```
Tests performed:
- Internet connectivity
- Cronlytic API reachability
- DNS resolution
- SSL certificate validation
- Response time measurement
```

### 2. **Authentication Diagnostics**
```
Validation checks:
- API key format and validity
- User ID format and access
- Permission levels
- Token expiration status
```

### 3. **Configuration Diagnostics**
```
Configuration review:
- Environment variables
- Claude Desktop integration
- MCP server settings
- JSON syntax validation
```

### 4. **Performance Diagnostics**
```
Performance analysis:
- Response time trends
- Success/failure rates
- Resource utilization
- Bottleneck identification
```

### 5. **Job Health Diagnostics**
```
Job-specific checks:
- Individual job status
- Schedule validation
- Endpoint connectivity
- Error frequency analysis
```

## 🚨 Issue Detection

### Automatic Issue Detection
- **Critical**: System non-functional, immediate attention needed
- **High**: Significant impact on operations
- **Medium**: Performance degradation or reliability issues
- **Low**: Minor optimizations or maintenance recommendations

### Common Issues Detected
- Failed authentication
- Broken webhook endpoints
- Schedule conflicts
- Performance bottlenecks
- Configuration errors

## 📈 Health Scoring

### Overall System Health Score (0-100)
- **90-100**: Excellent - System running optimally
- **80-89**: Good - Minor issues or optimizations possible
- **70-79**: Fair - Some attention needed
- **60-69**: Poor - Significant issues present
- **Below 60**: Critical - Immediate action required

### Component Health Breakdown
- **API Connectivity**: Connection reliability and speed
- **Authentication**: Credential validity and permissions
- **Job Performance**: Success rates and execution reliability
- **Configuration**: Setup correctness and optimization
- **System Resources**: Performance and capacity metrics

## 🔧 Recommended Actions

### Immediate Actions (if issues found)
1. **Fix critical errors** that prevent system operation
2. **Resolve authentication issues** for security
3. **Address failing jobs** to prevent data loss
4. **Update configurations** for stability

### Optimization Opportunities
1. **Improve job schedules** for better distribution
2. **Optimize API calls** for better performance
3. **Enhance error handling** for reliability
4. **Update configurations** for efficiency

### Preventive Maintenance
1. **Schedule regular health checks**
2. **Monitor key metrics** proactively
3. **Keep credentials current**
4. **Review and update configurations**

## 🚀 Quick Diagnostic Commands

**Start Here:**
- "Run a quick health check on my system"
- "Diagnose why my jobs are failing"
- "Check my system configuration"

**Specific Issues:**
- "My authentication keeps failing"
- "Jobs are running slower than usual"
- "I'm getting connection timeouts"

**Performance Analysis:**
- "Analyze my job performance over the last week"
- "Find optimization opportunities"
- "Check for system bottlenecks"

**Comprehensive Review:**
- "Perform a full system diagnostic"
- "Generate a health report for management"
- "Prepare a maintenance plan"

---

**Ready for diagnostics?** Tell me what level of analysis you need and any specific issues you're experiencing, and I'll provide detailed insights and actionable recommendations.
"""
}

# Error Analysis Prompt
ERROR_ANALYSIS_PROMPT = {
    "name": "error_analysis_guide",
    "description": "Advanced error pattern analysis and resolution guide",
    "arguments": [
        {
            "name": "error_type",
            "description": "Type of errors to analyze",
            "required": False
        },
        {
            "name": "time_period",
            "description": "Time period for error analysis",
            "required": False
        }
    ],
    "template": """# Error Analysis & Resolution Guide

I'll help you analyze error patterns, identify root causes, and implement effective solutions.

## 🔍 Error Analysis Overview

**Error Type:** {error_type}
**Time Period:** {time_period}

### Error Categories

**🚫 Connection Errors**
- Network timeouts
- DNS resolution failures
- SSL/TLS certificate issues
- Firewall blocks

**🔐 Authentication Errors**
- Invalid API keys
- Expired tokens
- Permission denied
- Rate limiting

**⚙️ Configuration Errors**
- Invalid job settings
- Malformed cron expressions
- Missing required fields
- JSON syntax errors

**🌐 Endpoint Errors**
- HTTP 4xx client errors
- HTTP 5xx server errors
- Webhook unavailable
- Response format issues

## 📊 Error Pattern Analysis

### Frequency Analysis
- **Error distribution** over time
- **Peak failure periods** identification
- **Recurring error patterns**
- **Success vs failure ratios**

### Root Cause Investigation
- **Common error sources**
- **Environmental factors**
- **Configuration changes correlation**
- **External dependency issues**

### Impact Assessment
- **Business impact** of different error types
- **Recovery time** for various issues
- **Resource costs** of errors
- **User experience impact**

## 🛠️ Resolution Strategies

### Immediate Resolution
1. **Pause failing jobs** to prevent cascading issues
2. **Fix critical errors** blocking system operation
3. **Restore service** with temporary workarounds
4. **Monitor recovery** and validate fixes

### Long-term Prevention
1. **Implement robust error handling**
2. **Add retry logic** with exponential backoff
3. **Set up monitoring** and alerting
4. **Create runbooks** for common issues

### Proactive Measures
1. **Regular health checks**
2. **Configuration validation**
3. **Dependency monitoring**
4. **Capacity planning**

## 🚨 Common Error Solutions

### "Connection Timeout"
**Root Causes:**
- Network latency or instability
- Server overload
- Firewall blocking requests

**Solutions:**
- Increase timeout values
- Implement retry logic
- Check network configuration
- Monitor server performance

### "Authentication Failed"
**Root Causes:**
- Expired credentials
- Wrong authentication method
- Missing permissions

**Solutions:**
- Refresh API keys
- Verify authentication format
- Check permission levels
- Test with different credentials

### "Webhook Unavailable"
**Root Causes:**
- Endpoint server down
- URL changed or moved
- SSL certificate expired

**Solutions:**
- Verify endpoint availability
- Update webhook URLs
- Check SSL certificates
- Implement fallback endpoints

## 📈 Error Metrics & KPIs

### Key Metrics to Track
- **Error Rate**: Percentage of failed requests
- **Mean Time to Recovery**: Average time to fix issues
- **Error Frequency**: Number of errors per time period
- **Success Rate**: Percentage of successful operations

### Performance Targets
- **Error Rate**: < 5%
- **Recovery Time**: < 30 minutes
- **Uptime**: > 99.5%
- **Response Time**: < 2 seconds

## 🔧 Monitoring & Alerting

### Alert Thresholds
- **Critical**: Error rate > 25% or system down
- **High**: Error rate > 10% or key jobs failing
- **Medium**: Error rate > 5% or performance degraded
- **Low**: Minor issues or optimization opportunities

### Monitoring Setup
```python
# Example monitoring configuration
ALERT_RULES = {
    "high_error_rate": {
        "condition": "error_rate > 0.10",
        "window": "5m",
        "action": "immediate_alert"
    },
    "authentication_failures": {
        "condition": "auth_errors > 5",
        "window": "1h",
        "action": "security_alert"
    },
    "slow_responses": {
        "condition": "avg_response_time > 5000",
        "window": "10m",
        "action": "performance_alert"
    }
}
```

---

**Ready for error analysis?** Tell me about the errors you're experiencing and I'll help identify patterns and provide targeted solutions.
"""
}

# Performance Optimization Prompt
PERFORMANCE_OPTIMIZATION_PROMPT = {
    "name": "performance_optimization",
    "description": "Comprehensive performance analysis and optimization guide",
    "arguments": [
        {
            "name": "optimization_focus",
            "description": "Area to focus optimization efforts on",
            "required": False
        },
        {
            "name": "performance_metric",
            "description": "Specific performance metric to improve",
            "required": False
        }
    ],
    "template": """# Performance Optimization Guide

I'll help you analyze and optimize your Cronlytic MCP server performance for maximum efficiency and reliability.

## 🚀 Optimization Overview

**Focus Area:** {optimization_focus}
**Target Metric:** {performance_metric}

### Performance Metrics

**📊 Response Metrics**
- API response times
- Job execution duration
- System throughput
- Resource utilization

**✅ Reliability Metrics**
- Success rates
- Error frequencies
- Uptime percentages
- Recovery times

**🔄 Efficiency Metrics**
- Resource consumption
- Cost per operation
- Scalability measures
- Automation levels

## 🎯 Optimization Areas

### 1. **API Performance**
- Reduce response times
- Optimize request patterns
- Implement caching
- Connection pooling

### 2. **Job Scheduling**
- Distribute load evenly
- Avoid timing conflicts
- Optimize frequencies
- Balance resource usage

### 3. **Error Handling**
- Reduce failure rates
- Faster error recovery
- Better retry strategies
- Proactive monitoring

### 4. **Resource Efficiency**
- Memory optimization
- CPU usage reduction
- Network efficiency
- Storage optimization

## 🔧 Optimization Strategies

### Quick Wins (Immediate Impact)
1. **Adjust job schedules** to avoid peak times
2. **Increase timeout values** for slow endpoints
3. **Enable connection reuse** for better performance
4. **Cache frequently used data**

### Medium-term Improvements
1. **Implement retry logic** with exponential backoff
2. **Optimize webhook endpoints** for faster responses
3. **Add monitoring dashboards** for better visibility
4. **Automate common maintenance tasks**

### Long-term Optimizations
1. **Redesign job architecture** for scalability
2. **Implement advanced caching strategies**
3. **Add predictive monitoring** and alerting
4. **Develop performance benchmarking**

## 📈 Performance Benchmarks

### Response Time Targets
- **Excellent**: < 200ms
- **Good**: 200ms - 1000ms
- **Acceptable**: 1000ms - 3000ms
- **Needs Improvement**: > 3000ms

### Success Rate Targets
- **Excellent**: > 99%
- **Good**: 95% - 99%
- **Acceptable**: 90% - 95%
- **Needs Improvement**: < 90%

### Efficiency Metrics
- **Resource utilization**: < 70%
- **Cost per operation**: Minimize
- **Scalability factor**: > 10x capacity
- **Automation level**: > 80%

## 🛠️ Optimization Tools

### Built-in Optimization
```python
# Configure performance settings
CRONLYTIC_CONFIG = {
    "timeout": 30,
    "max_retries": 3,
    "connection_pool_size": 10,
    "cache_ttl": 300,
    "enable_compression": True
}
```

### Monitoring & Analysis
```python
# Performance monitoring example
def monitor_performance():
    metrics = {
        "response_times": [],
        "success_rates": {},
        "error_patterns": {},
        "resource_usage": {}
    }

    # Collect and analyze metrics
    return generate_optimization_recommendations(metrics)
```

---

**Ready to optimize?** Tell me what performance challenges you're facing and I'll provide specific optimization strategies.
"""
}

# Maintenance Guide Prompt
MAINTENANCE_GUIDE_PROMPT = {
    "name": "maintenance_guide",
    "description": "Preventive maintenance and system care best practices guide",
    "arguments": [
        {
            "name": "maintenance_type",
            "description": "Type of maintenance needed",
            "required": False
        },
        {
            "name": "schedule",
            "description": "Maintenance schedule preference",
            "required": False
        }
    ],
    "template": """# System Maintenance Guide

I'll help you establish and execute effective maintenance routines to keep your Cronlytic MCP server running optimally.

## 🔧 Maintenance Overview

**Maintenance Type:** {maintenance_type}
**Schedule:** {schedule}

### Maintenance Categories

**🚀 Daily Maintenance (5-10 minutes)**
- Health check execution
- Error log review
- Critical alert monitoring
- Quick performance check

**📊 Weekly Maintenance (30-60 minutes)**
- Comprehensive system review
- Performance analysis
- Configuration optimization
- Security updates

**🔄 Monthly Maintenance (2-4 hours)**
- Deep system analysis
- Capacity planning review
- Documentation updates
- Disaster recovery testing

**🔧 Quarterly Maintenance (Half day)**
- Architecture review
- Security audit
- Performance benchmarking
- Strategic planning

## 📅 Maintenance Checklists

### Daily Checklist
- [ ] Run system health check
- [ ] Review overnight job executions
- [ ] Check for any critical errors
- [ ] Verify authentication status
- [ ] Monitor API response times

### Weekly Checklist
- [ ] Analyze job success rates
- [ ] Review error patterns
- [ ] Update job configurations if needed
- [ ] Check for system updates
- [ ] Validate backup systems

### Monthly Checklist
- [ ] Performance trend analysis
- [ ] Security review and updates
- [ ] Documentation maintenance
- [ ] Capacity planning assessment
- [ ] Disaster recovery testing

### Quarterly Checklist
- [ ] Comprehensive security audit
- [ ] Architecture optimization review
- [ ] Business requirements alignment
- [ ] Technology stack updates
- [ ] Strategic roadmap planning

## 🛠️ Maintenance Procedures

### Automated Maintenance
```python
# Example automated maintenance script
def daily_maintenance():
    tasks = [
        "health_check",
        "log_cleanup",
        "metrics_collection",
        "alert_review"
    ]

    for task in tasks:
        execute_maintenance_task(task)

def weekly_maintenance():
    tasks = [
        "performance_analysis",
        "security_scan",
        "configuration_backup",
        "capacity_review"
    ]

    for task in tasks:
        execute_maintenance_task(task)
```

### Manual Maintenance Tasks
1. **Credential Rotation**: Update API keys quarterly
2. **Configuration Review**: Validate settings monthly
3. **Performance Tuning**: Optimize based on metrics
4. **Documentation Updates**: Keep guides current

## 🔍 Preventive Measures

### Proactive Monitoring
- Set up automated health checks
- Configure performance alerts
- Monitor error rate trends
- Track resource utilization

### Regular Updates
- Keep dependencies current
- Apply security patches promptly
- Update configuration as needed
- Maintain documentation

### Capacity Planning
- Monitor growth trends
- Plan for scaling needs
- Optimize resource allocation
- Prepare for peak loads

---

**Ready for maintenance?** Tell me what type of maintenance you need help with and I'll provide detailed procedures and checklists.
"""
}