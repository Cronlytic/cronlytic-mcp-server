# Example Workflows and Usage Patterns

This document provides practical examples and common usage patterns for the Cronlytic MCP Server, demonstrating how to effectively use the server for various automation scenarios.

## Quick Start Examples

### 1. Health Check Monitoring

**Scenario**: Monitor your web application's health endpoint every 5 minutes.

```bash
# Using MCP client
create_job(
    name="api-health-check",
    url="https://api.yourapp.com/health",
    method="GET",
    headers={"User-Agent": "Cronlytic-Monitor"},
    body="",
    cron_expression="*/5 * * * *"
)
```

**Expected Response**:
```json
{
  "success": true,
  "job": {
    "job_id": "abc123-def456",
    "name": "api-health-check",
    "status": "pending",
    "next_run_at": "2025-01-20T10:05:00Z"
  },
  "message": "Job 'api-health-check' created successfully"
}
```

### 2. Daily Data Backup

**Scenario**: Trigger daily database backup at 2 AM.

```bash
# Create backup job
create_job(
    name="daily-db-backup",
    url="https://admin.yourapp.com/api/backup",
    method="POST",
    headers={
        "Authorization": "Bearer your-backup-token",
        "Content-Type": "application/json"
    },
    body='{"backup_type": "full", "notify": true}',
    cron_expression="0 2 * * *"
)
```

### 3. Weekly Report Generation

**Scenario**: Generate and email weekly reports every Monday at 9 AM.

```bash
create_job(
    name="weekly-analytics-report",
    url="https://analytics.yourapp.com/generate-report",
    method="POST",
    headers={"X-API-Key": "analytics-api-key"},
    body='{"report_type": "weekly", "format": "pdf", "email": true}',
    cron_expression="0 9 * * 1"
)
```

## Advanced Workflow Patterns

### 1. Multi-Step Webhook Chain

**Scenario**: Coordinate multiple services for a complex workflow.

```bash
# Step 1: Data processing job
create_job(
    name="process-daily-data",
    url="https://processor.yourapp.com/process",
    method="POST",
    headers={"Authorization": "Bearer token1"},
    body='{"date": "today", "next_webhook": "https://yourapp.com/next-step"}',
    cron_expression="0 1 * * *"
)

# Step 2: Notification service (triggered by step 1)
create_job(
    name="send-process-notifications",
    url="https://notifications.yourapp.com/send",
    method="POST",
    headers={"X-Service-Token": "notify-token"},
    body='{"template": "process_complete", "priority": "normal"}',
    cron_expression="0 2 * * *"
)
```

### 2. API Rate Limit Management

**Scenario**: Respect third-party API rate limits with staggered calls.

```bash
# Primary sync every hour
create_job(
    name="hourly-sync-primary",
    url="https://external-api.com/sync",
    method="GET",
    headers={"X-API-Key": "external-key"},
    cron_expression="0 * * * *"
)

# Secondary sync offset by 30 minutes
create_job(
    name="hourly-sync-secondary",
    url="https://external-api.com/sync-secondary",
    method="GET",
    headers={"X-API-Key": "external-key"},
    cron_expression="30 * * * *"
)
```

### 3. Conditional Webhook Execution

**Scenario**: Use webhook payloads to control execution logic.

```bash
create_job(
    name="conditional-cleanup",
    url="https://yourapp.com/cleanup",
    method="POST",
    headers={"Content-Type": "application/json"},
    body='{"check_conditions": true, "dry_run": false, "max_items": 1000}',
    cron_expression="0 0 * * 0"  # Weekly on Sunday
)
```

## Industry-Specific Examples

### E-commerce Platform

```bash
# Inventory sync every 15 minutes during business hours
create_job(
    name="inventory-sync",
    url="https://inventory.shop.com/sync",
    method="POST",
    headers={"Authorization": "Bearer shop-token"},
    body='{"sync_type": "incremental"}',
    cron_expression="*/15 9-17 * * 1-5"
)

# Daily sales report
create_job(
    name="daily-sales-report",
    url="https://analytics.shop.com/sales-report",
    method="POST",
    headers={"X-Report-Key": "analytics-key"},
    body='{"period": "daily", "email_recipients": ["manager@shop.com"]}',
    cron_expression="0 18 * * *"
)

# Weekly abandoned cart recovery
create_job(
    name="cart-recovery-campaign",
    url="https://marketing.shop.com/cart-recovery",
    method="POST",
    headers={"Authorization": "Bearer marketing-token"},
    body='{"campaign_type": "weekly", "min_cart_value": 50}',
    cron_expression="0 10 * * 2"
)
```

### SaaS Application

```bash
# Trial expiration notifications
create_job(
    name="trial-expiry-reminders",
    url="https://saas.app.com/trial-reminders",
    method="POST",
    headers={"X-Internal-Token": "internal-service-token"},
    body='{"reminder_type": "3_days", "include_upgrade_link": true}',
    cron_expression="0 9 * * *"
)

# Usage metrics calculation
create_job(
    name="usage-metrics-calculation",
    url="https://metrics.saas.app.com/calculate",
    method="POST",
    headers={"Authorization": "Bearer metrics-token"},
    body='{"period": "daily", "include_trends": true}',
    cron_expression="0 23 * * *"
)

# System health monitoring
create_job(
    name="system-health-check",
    url="https://monitoring.saas.app.com/health",
    method="GET",
    headers={"X-Monitor-Token": "health-check-token"},
    cron_expression="*/10 * * * *"
)
```

### DevOps & CI/CD

```bash
# Daily dependency security scan
create_job(
    name="security-dependency-scan",
    url="https://security.devops.com/scan",
    method="POST",
    headers={"Authorization": "Bearer security-token"},
    body='{"scan_type": "dependencies", "notify_on": "high_severity"}',
    cron_expression="0 2 * * *"
)

# Weekly infrastructure cost report
create_job(
    name="infrastructure-cost-report",
    url="https://billing.devops.com/cost-report",
    method="POST",
    headers={"X-Billing-Key": "cost-analysis-key"},
    body='{"period": "weekly", "breakdown": "by_service", "format": "detailed"}',
    cron_expression="0 8 * * 1"
)

# Automated database maintenance
create_job(
    name="db-maintenance-routine",
    url="https://db-admin.devops.com/maintenance",
    method="POST",
    headers={"Authorization": "Bearer db-admin-token"},
    body='{"operations": ["vacuum", "reindex"], "backup_first": true}',
    cron_expression="0 3 * * 0"
)
```

## Error Handling Patterns

### Robust Error Recovery

```bash
# Main job with error handling
create_job(
    name="data-sync-with-recovery",
    url="https://sync.yourapp.com/sync",
    method="POST",
    headers={
        "Authorization": "Bearer sync-token",
        "X-Retry-Policy": "exponential"
    },
    body='{"max_retries": 3, "fallback_endpoint": "https://backup.yourapp.com/sync"}',
    cron_expression="0 */4 * * *"
)
```

### Health Check with Alerting

```bash
create_job(
    name="critical-service-health",
    url="https://monitor.yourapp.com/critical-check",
    method="POST",
    headers={"X-Alert-Channel": "slack"},
    body='{"services": ["database", "cache", "queue"], "alert_on_failure": true}',
    cron_expression="*/2 * * * *"
)
```

## Performance Optimization Patterns

### Batch Processing

```bash
# Process in batches to avoid overwhelming the system
create_job(
    name="batch-user-sync",
    url="https://users.yourapp.com/batch-sync",
    method="POST",
    headers={"Content-Type": "application/json"},
    body='{"batch_size": 1000, "parallel_workers": 5}',
    cron_expression="0 */6 * * *"
)
```

### Off-Peak Processing

```bash
# Heavy processing during off-peak hours
create_job(
    name="heavy-data-processing",
    url="https://processing.yourapp.com/heavy-job",
    method="POST",
    headers={"X-Priority": "low"},
    body='{"process_type": "full_rebuild", "optimize_for": "thoroughness"}',
    cron_expression="0 2 * * 0"  # 2 AM on Sundays
)
```

## Monitoring and Debugging Workflows

### Get Job Status and Logs

```bash
# Check specific job
get_job(job_id="abc123-def456")

# Get execution logs
get_job_logs(job_id="abc123-def456")

# List all jobs with filtering
list_jobs(include_paused=false, limit=20)
```

### Job Management Operations

```bash
# Temporarily pause a job
pause_job(job_id="abc123-def456")

# Resume a paused job
resume_job(job_id="abc123-def456")

# Update job schedule
update_job(
    job_id="abc123-def456",
    name="updated-job-name",
    url="https://new-endpoint.com/webhook",
    method="POST",
    headers={"Authorization": "Bearer new-token"},
    body='{"updated": true}',
    cron_expression="0 */2 * * *"  # Every 2 hours instead of every 4
)

# Delete job when no longer needed
delete_job(job_id="abc123-def456")
```

## Common Cron Expression Patterns

### Frequently Used Schedules

```bash
# Every 5 minutes
"*/5 * * * *"

# Every hour at minute 0
"0 * * * *"

# Every day at 6 AM
"0 6 * * *"

# Every Monday at 9 AM
"0 9 * * 1"

# First day of every month at midnight
"0 0 1 * *"

# Every weekday at 2:30 PM
"30 14 * * 1-5"

# Every 6 hours
"0 */6 * * *"

# Twice daily at 9 AM and 6 PM
"0 9,18 * * *"
```

### Business-Specific Schedules

```bash
# Business hours only (9 AM - 5 PM, weekdays)
"0 9-17 * * 1-5"

# End of business day
"0 17 * * 1-5"

# Weekend processing
"0 8 * * 6,0"

# Monthly reporting (first Monday of each month at 9 AM)
"0 9 1-7 * 1"

# Quarterly maintenance (first Sunday of Jan, Apr, Jul, Oct at 2 AM)
"0 2 1-7 1,4,7,10 0"
```

## Troubleshooting Common Issues

### Job Not Running

1. Check job status: `get_job(job_id="your-job-id")`
2. Verify cron expression: Use tools like [crontab.guru](https://crontab.guru)
3. Check logs: `get_job_logs(job_id="your-job-id")`
4. Ensure webhook endpoint is accessible

### Authentication Failures

```bash
# Test webhook endpoint manually
curl -X POST "https://your-endpoint.com/webhook" \
  -H "Authorization: Bearer your-token" \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### Performance Issues

1. Check execution logs for response times
2. Consider adjusting cron frequency
3. Optimize webhook endpoint performance
4. Use batch processing for large operations

## Best Practices Summary

### Security
- Use HTTPS endpoints only
- Implement proper authentication tokens
- Rotate API keys regularly
- Don't include sensitive data in job names

### Reliability
- Implement idempotent webhook endpoints
- Use appropriate timeout values
- Include error handling in webhooks
- Monitor job execution logs regularly

### Performance
- Avoid excessive frequency for non-critical jobs
- Use off-peak hours for heavy processing
- Implement efficient webhook endpoints
- Consider batch processing for large datasets

### Maintenance
- Document your job purposes and dependencies
- Use descriptive job names
- Regularly review and clean up unused jobs
- Monitor job execution patterns

## Integration Examples

### With Popular Services

#### Slack Integration
```bash
create_job(
    name="daily-team-standup-reminder",
    url="https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK",
    method="POST",
    headers={"Content-Type": "application/json"},
    body='{"text": "🌅 Good morning team! Time for daily standup in 15 minutes."}',
    cron_expression="45 8 * * 1-5"
)
```

#### Discord Webhook
```bash
create_job(
    name="server-maintenance-notification",
    url="https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK",
    method="POST",
    headers={"Content-Type": "application/json"},
    body='{"content": "🔧 Scheduled server maintenance starting now."}',
    cron_expression="0 2 * * 0"
)
```

#### Email Service (via API)
```bash
create_job(
    name="weekly-newsletter",
    url="https://api.mailgun.net/v3/yourdomain.com/messages",
    method="POST",
    headers={"Authorization": "Basic YOUR_MAILGUN_KEY"},
    body='{"from": "newsletter@yourdomain.com", "to": "subscribers@yourdomain.com", "subject": "Weekly Update", "template": "weekly-template"}',
    cron_expression="0 10 * * 1"
)
```

This comprehensive guide should help users understand how to effectively use the Cronlytic MCP Server for various automation scenarios, from simple health checks to complex multi-step workflows.