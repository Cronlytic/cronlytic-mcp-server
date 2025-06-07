"""Job management prompts for the Cronlytic MCP Server."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class JobManagementPrompts:
    """Interactive prompts for job management workflows."""

    @staticmethod
    def get_prompts() -> List[Dict[str, Any]]:
        """Get all job management prompts."""
        return [
            CREATE_JOB_PROMPT,
            UPDATE_JOB_PROMPT,
            JOB_MONITORING_PROMPT,
            JOB_TROUBLESHOOTING_PROMPT,
            BULK_JOB_MANAGEMENT_PROMPT,
        ]


# Create Job Interactive Flow
CREATE_JOB_PROMPT = {
    "name": "create_job_flow",
    "description": "Interactive flow to create a new cron job with step-by-step guidance",
    "arguments": [
        {
            "name": "job_type",
            "description": "Type of job to create",
            "required": False
        },
        {
            "name": "complexity",
            "description": "Complexity level: basic, intermediate, or advanced",
            "required": False
        }
    ],
    "template": """# Create a New Cron Job

I'll help you create a new cron job step by step. Let me guide you through the process based on your needs.

## Step 1: Job Purpose
First, let's understand what you want to achieve:

**Common job types:**
- 🔍 **API Monitoring** - Health checks and endpoint monitoring
- 💾 **Data Backup** - Database or file system backups
- 📊 **Report Generation** - Automated reports and notifications
- 🔄 **Data Synchronization** - ETL processes and data updates
- 🧹 **Cleanup Tasks** - Log rotation, cache clearing
- 📧 **Notifications** - Alert systems and reminders
- 🔧 **Custom Webhook** - Custom HTTP requests

**What type of job do you want to create?** {job_type}

## Step 2: Basic Configuration

Once I understand your job type, I'll help you configure:

### Job Details
- **Name**: A descriptive name for your job (alphanumeric, hyphens, underscores only)
- **Description**: What this job does and why it's important
- **URL**: The endpoint to call when the job runs
- **HTTP Method**: GET, POST, PUT, DELETE, etc.

### Schedule Configuration
I'll help you choose the right schedule using:
- **Common patterns** (every 5 min, hourly, daily, weekly)
- **Business schedules** (weekdays only, business hours)
- **Custom expressions** (advanced cron syntax)

### Optional Enhancements
- **Headers**: Authentication tokens, content types
- **Request Body**: POST data, JSON payloads
- **Error Handling**: Retry policies, failure notifications

## Step 3: Validation & Testing

Before creating the job, I'll:
- ✅ Validate all configuration
- ⚡ Test the webhook endpoint
- 📅 Show next execution times
- 🔍 Preview the complete job configuration

## Step 4: Creation & Monitoring

After creation, I'll help you:
- 📋 Review the created job details
- 📊 Set up monitoring and alerts
- 🔧 Test the first execution
- 📝 Document the job for your team

---

**Ready to start?** Tell me about the job you want to create, and I'll guide you through each step with specific recommendations based on your use case.

**Example starter prompts:**
- "I want to monitor my API every 5 minutes"
- "I need to backup my database daily at 2 AM"
- "I want to generate weekly reports every Friday"
- "I need to sync data between systems every hour"

**Need help with cron schedules?** I can show you common patterns and help you build custom expressions.
"""
}

# Update Job Prompt
UPDATE_JOB_PROMPT = {
    "name": "update_job_flow",
    "description": "Interactive flow to update existing cron jobs with guided assistance",
    "arguments": [
        {
            "name": "job_id",
            "description": "ID of the job to update",
            "required": False
        },
        {
            "name": "update_type",
            "description": "Type of update needed",
            "required": False
        }
    ],
    "template": """# Update Existing Cron Job

I'll help you safely update your cron job with step-by-step guidance and validation.

## Step 1: Job Selection
{job_id}

Let me help you identify the job to update:

**Available actions:**
- 📋 List all your jobs with current status
- 🔍 Search jobs by name or description
- 📊 Show job details and current configuration
- ⏰ Display recent execution history

## Step 2: Update Planning

**Common update scenarios:**
- ⏰ **Schedule Changes** - Modify execution frequency or timing
- 🔗 **Endpoint Updates** - Change URL or HTTP method
- 🔧 **Configuration Tweaks** - Update headers, body, or parameters
- ⏸️ **Pause/Resume** - Temporarily disable or re-enable
- 🏷️ **Metadata Updates** - Change name or description

**What do you want to update?** {update_type}

## Step 3: Safe Update Process

### Pre-Update Validation
- 📋 Show current job configuration
- ⚠️ Identify potential breaking changes
- 🔍 Validate new configuration
- ⏰ Preview schedule changes

### Change Preview
- 📊 Before/after comparison
- 📅 Next execution time changes
- ⚡ Impact assessment
- 🔄 Rollback planning

### Update Execution
- ✅ Apply changes safely
- 📊 Verify update success
- 🔍 Test new configuration
- 📝 Document changes

## Step 4: Post-Update Verification

After updating, I'll help you:
- ✅ Confirm the update was successful
- 📊 Monitor first execution with new settings
- 🔍 Verify endpoint connectivity
- 📝 Update your documentation

---

**Update Types Quick Reference:**

**⏰ Schedule Updates:**
- Change frequency (every 5 min → every hour)
- Adjust timing (9 AM → 6 PM)
- Modify days (daily → weekdays only)

**🔗 Endpoint Updates:**
- New URL or domain
- Different HTTP method
- Updated authentication

**⚡ Quick Actions:**
- Pause job temporarily
- Resume paused job
- Test current configuration

**🆘 Emergency Actions:**
- Immediately pause failing job
- Fix broken configuration
- Restore from backup

---

**Ready to update?** Tell me which job you want to modify and what changes you need to make.

**Example commands:**
- "Update job job-123 to run every hour instead of every 30 minutes"
- "Change the URL for my API monitoring job"
- "Pause my backup job temporarily"
- "Show me all jobs that haven't run successfully recently"
"""
}

# Job Monitoring Prompt
JOB_MONITORING_PROMPT = {
    "name": "job_monitoring_dashboard",
    "description": "Comprehensive job monitoring and health dashboard guide",
    "arguments": [
        {
            "name": "time_range",
            "description": "Time range for monitoring data",
            "required": False
        },
        {
            "name": "focus_area",
            "description": "Specific area to focus on",
            "required": False
        }
    ],
    "template": """# Job Monitoring Dashboard

Get a comprehensive view of your cron job health, performance, and status.

## 📊 Quick Health Overview

**System Status:**
- 🟢 Active Jobs: Running and scheduled
- 🟡 Paused Jobs: Temporarily disabled
- 🔴 Failed Jobs: Recent failures needing attention
- ⏰ Upcoming: Next jobs to execute

## 🔍 Monitoring Categories

### 1. **Job Health Monitoring**
- **Success Rate**: Track job execution success percentage
- **Failure Analysis**: Identify patterns in job failures
- **Performance Trends**: Response times and execution duration
- **Reliability Metrics**: Uptime and consistency tracking

### 2. **Schedule Monitoring**
- **Execution Timeline**: When jobs last ran and next runs
- **Schedule Conflicts**: Overlapping or conflicting schedules
- **Missed Executions**: Jobs that failed to run on schedule
- **Frequency Analysis**: Job execution patterns over time

### 3. **Endpoint Health**
- **Response Monitoring**: HTTP status codes and response times
- **Connectivity Issues**: Network and DNS problems
- **Authentication Status**: Token expiration and auth failures
- **Payload Validation**: Request/response format issues

### 4. **Operational Insights**
- **Resource Usage**: API call quotas and rate limiting
- **Error Patterns**: Common failure types and causes
- **Performance Optimization**: Slow jobs and bottlenecks
- **Capacity Planning**: Job growth and system scaling

## 📈 Monitoring Time Ranges
{time_range}

**Available time ranges:**
- **Last 24 hours** - Recent performance and immediate issues
- **Last 7 days** - Weekly patterns and trends
- **Last 30 days** - Monthly overview and long-term health
- **Custom range** - Specific time period analysis

## 🎯 Focus Areas
{focus_area}

**Monitoring focus options:**
- 🚨 **Critical Issues** - Failed jobs and urgent problems
- 📊 **Performance** - Response times and efficiency metrics
- 📅 **Scheduling** - Timeline and frequency analysis
- 🔍 **Troubleshooting** - Diagnostic information and root cause analysis

## 🔧 Available Actions

### Immediate Actions
- 📋 **List all jobs** with current status
- 🔍 **Get detailed job info** including recent logs
- ⏸️ **Pause failing jobs** to prevent further issues
- ▶️ **Resume healthy jobs** that were paused

### Analysis Tools
- 📊 **Generate health report** with comprehensive metrics
- 🔍 **Analyze failure patterns** to identify common issues
- 📈 **Performance analysis** for optimization opportunities
- 📅 **Schedule optimization** suggestions

### Maintenance Actions
- 🧹 **Clean up old logs** and historical data
- 🔄 **Update job configurations** based on performance
- 📝 **Export monitoring data** for external analysis
- 🔔 **Set up alerts** for proactive monitoring

---

## 🚀 Quick Start Commands

**Get overall health:**
- "Show me a summary of all my jobs"
- "List any jobs that have failed recently"
- "What jobs are running right now?"

**Analyze specific issues:**
- "Why did job X fail last night?"
- "Show me jobs with poor success rates"
- "Which jobs are taking too long to complete?"

**Performance optimization:**
- "Which jobs should I optimize first?"
- "Show me jobs that could be scheduled better"
- "What are my heaviest resource consumers?"

**Proactive monitoring:**
- "Set up alerts for critical job failures"
- "Show me jobs that might fail soon"
- "What maintenance should I perform this week?"

---

**Ready to monitor?** Tell me what aspect of your jobs you'd like to focus on, and I'll provide detailed insights and actionable recommendations.
"""
}

# Troubleshooting Prompt
JOB_TROUBLESHOOTING_PROMPT = {
    "name": "job_troubleshooting_guide",
    "description": "Comprehensive troubleshooting assistance for job issues",
    "arguments": [
        {
            "name": "issue_type",
            "description": "Type of issue encountered",
            "required": False
        },
        {
            "name": "job_id",
            "description": "Specific job having issues",
            "required": False
        }
    ],
    "template": """# Job Troubleshooting Assistant

I'll help you diagnose and fix issues with your cron jobs using systematic troubleshooting approaches.

## 🔍 Issue Identification

**What's the problem?** {issue_type}

### Common Issue Categories:

**🚫 Job Not Running**
- Job appears stuck or never executes
- Schedule seems correct but no execution
- Job was working but stopped

**❌ Job Failing**
- Job runs but returns errors
- HTTP errors (4xx, 5xx status codes)
- Timeout or connection issues

**⏰ Timing Issues**
- Job runs at wrong times
- Schedule conflicts or overlaps
- Missed executions

**🔗 Endpoint Problems**
- Webhook URL not responding
- Authentication failures
- Payload or format issues

**📊 Performance Issues**
- Jobs taking too long
- High failure rates
- Resource consumption problems

## 🛠️ Diagnostic Tools

### Step 1: Basic Health Check
```
Let me check your job's current status:
- Current configuration and schedule
- Recent execution history
- Last known error messages
- Endpoint connectivity test
```

### Step 2: Deep Diagnostics
```
Advanced troubleshooting:
- Detailed error log analysis
- Network connectivity tests
- Authentication validation
- Schedule conflict detection
```

### Step 3: Root Cause Analysis
```
Identify the underlying issue:
- Pattern recognition in failures
- Timeline correlation analysis
- Configuration validation
- External dependency checks
```

## 🚨 Common Issues & Solutions

### Issue: "Job Not Executing"
**Symptoms:** Job shows as active but never runs
**Diagnostic Steps:**
1. Check job status and schedule
2. Verify cron expression syntax
3. Look for system-level issues
4. Check for job conflicts

**Common Causes:**
- Invalid cron expression
- Job is paused
- Schedule conflicts
- System maintenance

**Solutions:**
- Validate and fix cron expression
- Resume paused jobs
- Adjust conflicting schedules
- Check system status

### Issue: "Job Failing with HTTP Errors"
**Symptoms:** Job runs but returns 4xx/5xx errors
**Diagnostic Steps:**
1. Test endpoint manually
2. Check authentication
3. Validate request format
4. Review response headers

**Common Causes:**
- Expired authentication tokens
- Changed API endpoints
- Invalid request format
- Rate limiting

**Solutions:**
- Update authentication credentials
- Fix endpoint URLs
- Correct request format
- Implement rate limiting

### Issue: "Intermittent Failures"
**Symptoms:** Job sometimes works, sometimes fails
**Diagnostic Steps:**
1. Analyze failure patterns
2. Check external dependencies
3. Monitor timing issues
4. Review error frequency

**Common Causes:**
- Network instability
- Endpoint overload
- Timing race conditions
- Resource constraints

**Solutions:**
- Implement retry logic
- Add error handling
- Adjust timing/frequency
- Scale resources

## 🔧 Troubleshooting Workflow

### Quick Diagnostics (2-5 minutes)
1. **Status Check**: Is the job active and scheduled?
2. **Recent Logs**: What do the last few executions show?
3. **Endpoint Test**: Can we reach the webhook URL?
4. **Auth Check**: Are credentials valid?

### Detailed Analysis (10-15 minutes)
1. **Historical Patterns**: When did issues start?
2. **Configuration Review**: Compare working vs. broken state
3. **Dependency Check**: Are external services healthy?
4. **Performance Analysis**: Are there resource constraints?

### Advanced Troubleshooting (30+ minutes)
1. **Root Cause Analysis**: Deep dive into underlying issues
2. **Environment Comparison**: Test vs. production differences
3. **Load Testing**: Can the system handle current volume?
4. **Architecture Review**: Are there design improvements needed?

## 🎯 Specific Job Troubleshooting
{job_id}

**For a specific job, I can:**
- 📊 Pull complete execution history
- 🔍 Analyze error patterns and trends
- ⚡ Test current configuration
- 🔧 Suggest specific fixes
- 📋 Provide step-by-step resolution

## 🚀 Prevention & Best Practices

### Proactive Monitoring
- Set up failure alerts
- Monitor success rates
- Track performance trends
- Regular health checks

### Robust Configuration
- Implement retry logic
- Add comprehensive error handling
- Use appropriate timeouts
- Validate all inputs

### Documentation & Maintenance
- Document job purposes and dependencies
- Regular configuration reviews
- Keep authentication current
- Plan for capacity growth

---

## 🆘 Emergency Troubleshooting

**Critical job failure?**
1. Pause the failing job immediately
2. Check if it's affecting other systems
3. Review recent changes
4. Implement temporary workaround
5. Plan permanent fix

**Need immediate help?**
- "My backup job failed - what should I do?"
- "All my monitoring jobs stopped working"
- "Job X is failing and I need it fixed ASAP"
- "Help me troubleshoot job failures from the last 24 hours"

---

**Ready to troubleshoot?** Tell me about the issue you're experiencing, and I'll guide you through a systematic diagnosis and resolution process.
"""
}

# Bulk Job Management Prompt
BULK_JOB_MANAGEMENT_PROMPT = {
    "name": "bulk_job_operations",
    "description": "Efficient management guide for multiple jobs with batch operations",
    "arguments": [
        {
            "name": "operation_type",
            "description": "Type of bulk operation to perform",
            "required": False
        },
        {
            "name": "job_filter",
            "description": "Criteria for selecting jobs",
            "required": False
        }
    ],
    "template": """# Bulk Job Management

Efficiently manage multiple cron jobs with batch operations, filtering, and bulk updates.

## 🎯 Bulk Operations

**What would you like to do?** {operation_type}

### Available Operations:

**📊 Analysis & Reporting**
- **Health Summary**: Overall status of all jobs
- **Performance Report**: Success rates, response times, trends
- **Schedule Analysis**: Timing conflicts, optimization opportunities
- **Failure Report**: Jobs with recent failures or issues

**🔧 Batch Updates**
- **Schedule Changes**: Update timing for multiple jobs
- **Configuration Updates**: Change URLs, headers, or methods
- **Authentication Refresh**: Update API keys or tokens
- **Bulk Pause/Resume**: Control multiple jobs simultaneously

**🧹 Maintenance Operations**
- **Cleanup**: Remove old logs, archive inactive jobs
- **Optimization**: Improve schedules and configurations
- **Validation**: Check all jobs for issues
- **Backup**: Export job configurations

## 🔍 Job Selection & Filtering
{job_filter}

### Smart Filtering Options:

**By Status:**
- Active jobs only
- Paused jobs only
- Failed jobs (recent failures)
- Successful jobs (high success rate)

**By Schedule:**
- Jobs running hourly/daily/weekly
- Jobs with specific timing
- Conflicting schedules
- Underutilized schedules

**By Performance:**
- High-failure-rate jobs
- Slow-response jobs
- Resource-heavy jobs
- Recently created jobs

**By Purpose:**
- Monitoring jobs
- Backup jobs
- Notification jobs
- Custom categories

## 📋 Bulk Operation Workflows

### 1. **Bulk Health Check**
```
Operation: Comprehensive health analysis
Process:
1. Gather all job data
2. Analyze success rates and patterns
3. Identify problematic jobs
4. Generate prioritized action list
5. Provide optimization recommendations
```

### 2. **Batch Configuration Update**
```
Operation: Update multiple jobs safely
Process:
1. Select jobs by criteria
2. Preview proposed changes
3. Validate new configurations
4. Apply changes with rollback option
5. Verify updates and monitor results
```

### 3. **Schedule Optimization**
```
Operation: Improve job scheduling
Process:
1. Analyze current schedules
2. Identify conflicts and inefficiencies
3. Propose optimized timing
4. Preview impact on system load
5. Implement optimized schedules
```

### 4. **Bulk Troubleshooting**
```
Operation: Fix multiple job issues
Process:
1. Identify all failing jobs
2. Categorize failure types
3. Apply common fixes
4. Test and validate repairs
5. Monitor ongoing health
```

## 🚀 Quick Bulk Actions

### Emergency Operations
- **"Pause all failing jobs"** - Immediately stop problematic jobs
- **"Resume all healthy jobs"** - Restart paused jobs that are working
- **"Fix authentication for all jobs"** - Update expired credentials
- **"Generate emergency health report"** - Quick system overview

### Maintenance Operations
- **"Optimize all job schedules"** - Reduce conflicts and improve efficiency
- **"Update all monitoring jobs to run every 5 minutes"** - Batch schedule change
- **"Clean up jobs that haven't run in 30 days"** - Archive old jobs
- **"Backup all job configurations"** - Export for safekeeping

### Analysis Operations
- **"Show me all jobs with success rate below 90%"** - Identify problem jobs
- **"Find jobs that could be consolidated"** - Optimization opportunities
- **"List jobs consuming the most resources"** - Performance analysis
- **"Generate monthly job performance report"** - Comprehensive analytics

## 📊 Bulk Operation Examples

### Example 1: Morning Health Check
```
Goal: Start the day with complete system overview
Steps:
1. Generate overnight execution report
2. Identify any failures or issues
3. Check upcoming job schedule
4. Provide prioritized action items
```

### Example 2: Schedule Optimization
```
Goal: Reduce system load and conflicts
Steps:
1. Analyze current job distribution
2. Identify peak usage times
3. Propose load balancing changes
4. Implement optimized schedules
```

### Example 3: Bulk Maintenance
```
Goal: Keep all jobs healthy and efficient
Steps:
1. Update expired authentication
2. Clean up old execution logs
3. Optimize underperforming jobs
4. Validate all configurations
```

## 🎯 Custom Bulk Operations

**Need something specific?** I can help with:

**Advanced Filtering:**
- Jobs created in the last week
- Jobs that haven't succeeded in 24 hours
- Jobs with specific URLs or patterns
- Jobs scheduled during business hours

**Complex Updates:**
- Migrate all jobs to new API endpoint
- Update authentication method for all jobs
- Change all daily jobs to different time
- Add new headers to all API calls

**Specialized Reports:**
- Cost analysis of job execution
- Security audit of job configurations
- Performance benchmarking
- Compliance checking

---

## 🔧 Getting Started

**Ready for bulk operations?** Here are some starter commands:

**Quick Health Check:**
- "Show me the status of all my jobs"
- "Which jobs need attention today?"
- "Generate a health report for all jobs"

**Batch Updates:**
- "Update all my monitoring jobs to use the new API key"
- "Change all daily backup jobs to run at 3 AM instead of 2 AM"
- "Pause all jobs that are currently failing"

**Optimization:**
- "Help me optimize my job schedules"
- "Find jobs that could be running more efficiently"
- "Show me the best times to schedule new jobs"

**Maintenance:**
- "Clean up old job logs and optimize performance"
- "Backup all my job configurations"
- "Check all jobs for potential issues"

---

**Tell me what bulk operation you need**, and I'll guide you through the most efficient approach to manage your jobs at scale.
"""
}