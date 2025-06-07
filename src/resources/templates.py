"""Cron templates resource for the Cronlytic MCP Server."""

import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class CronTemplatesProvider:
    """Provider for cron expression templates and patterns."""

    def __init__(self):
        """Initialize the cron templates provider."""
        self.base_uri = "cronlytic://templates/cron"
        self._templates = self._generate_templates()

    def _generate_templates(self) -> Dict[str, Any]:
        """Generate comprehensive cron expression templates."""
        return {
            "common_patterns": {
                "every_minute": {
                    "expression": "* * * * *",
                    "description": "Run every minute",
                    "next_runs": "Every minute at second 0",
                    "use_cases": ["Testing", "Frequent monitoring", "Real-time processing"]
                },
                "every_5_minutes": {
                    "expression": "*/5 * * * *",
                    "description": "Run every 5 minutes",
                    "next_runs": "At minute 0, 5, 10, 15, 20, etc.",
                    "use_cases": ["API health checks", "Quick data synchronization"]
                },
                "every_15_minutes": {
                    "expression": "*/15 * * * *",
                    "description": "Run every 15 minutes",
                    "next_runs": "At minute 0, 15, 30, 45 of every hour",
                    "use_cases": ["Regular monitoring", "Data updates"]
                },
                "every_30_minutes": {
                    "expression": "*/30 * * * *",
                    "description": "Run every 30 minutes",
                    "next_runs": "At minute 0 and 30 of every hour",
                    "use_cases": ["Moderate frequency tasks", "System checks"]
                },
                "hourly": {
                    "expression": "0 * * * *",
                    "description": "Run every hour at minute 0",
                    "next_runs": "At minute 0 of every hour",
                    "use_cases": ["Hourly reports", "Cache clearing", "Log rotation"]
                },
                "every_2_hours": {
                    "expression": "0 */2 * * *",
                    "description": "Run every 2 hours",
                    "next_runs": "At minute 0 of hour 0, 2, 4, 6, etc.",
                    "use_cases": ["Extended monitoring", "Batch processing"]
                },
                "every_6_hours": {
                    "expression": "0 */6 * * *",
                    "description": "Run every 6 hours",
                    "next_runs": "At 00:00, 06:00, 12:00, 18:00",
                    "use_cases": ["Quarterly daily tasks", "System maintenance"]
                },
                "daily_midnight": {
                    "expression": "0 0 * * *",
                    "description": "Run daily at midnight",
                    "next_runs": "At 00:00 every day",
                    "use_cases": ["Daily reports", "Database cleanup", "Backups"]
                },
                "daily_morning": {
                    "expression": "0 9 * * *",
                    "description": "Run daily at 9 AM",
                    "next_runs": "At 09:00 every day",
                    "use_cases": ["Morning reports", "Business hour tasks"]
                },
                "daily_evening": {
                    "expression": "0 18 * * *",
                    "description": "Run daily at 6 PM",
                    "next_runs": "At 18:00 every day",
                    "use_cases": ["End-of-day processing", "Evening reports"]
                }
            },
            "weekly_patterns": {
                "weekly_monday": {
                    "expression": "0 9 * * 1",
                    "description": "Run every Monday at 9 AM",
                    "next_runs": "At 09:00 on Monday",
                    "use_cases": ["Weekly reports", "Monday updates"]
                },
                "weekly_friday": {
                    "expression": "0 17 * * 5",
                    "description": "Run every Friday at 5 PM",
                    "next_runs": "At 17:00 on Friday",
                    "use_cases": ["End-of-week reports", "Weekly cleanup"]
                },
                "weekdays_only": {
                    "expression": "0 9 * * 1-5",
                    "description": "Run weekdays at 9 AM (Monday-Friday)",
                    "next_runs": "At 09:00 on Monday through Friday",
                    "use_cases": ["Business day tasks", "Workday notifications"]
                },
                "weekends_only": {
                    "expression": "0 10 * * 6,0",
                    "description": "Run weekends at 10 AM (Saturday and Sunday)",
                    "next_runs": "At 10:00 on Saturday and Sunday",
                    "use_cases": ["Weekend maintenance", "Off-hours processing"]
                }
            },
            "monthly_patterns": {
                "monthly_first": {
                    "expression": "0 9 1 * *",
                    "description": "Run on the 1st day of every month at 9 AM",
                    "next_runs": "At 09:00 on day-of-month 1",
                    "use_cases": ["Monthly reports", "Billing cycles", "Subscription renewals"]
                },
                "monthly_last": {
                    "expression": "0 9 28-31 * *",
                    "description": "Run on the last day of the month at 9 AM",
                    "next_runs": "At 09:00 on day-of-month 28 through 31",
                    "use_cases": ["End-of-month processing", "Monthly summaries"],
                    "note": "Will only run on the last valid day of each month"
                },
                "monthly_mid": {
                    "expression": "0 9 15 * *",
                    "description": "Run on the 15th of every month at 9 AM",
                    "next_runs": "At 09:00 on day-of-month 15",
                    "use_cases": ["Mid-month reports", "Bi-monthly cycles"]
                }
            },
            "special_patterns": {
                "twice_daily": {
                    "expression": "0 9,21 * * *",
                    "description": "Run twice daily at 9 AM and 9 PM",
                    "next_runs": "At 09:00 and 21:00",
                    "use_cases": ["Bi-daily synchronization", "Morning and evening tasks"]
                },
                "business_hours": {
                    "expression": "0 9-17 * * 1-5",
                    "description": "Run every hour during business hours (9 AM-5 PM, weekdays)",
                    "next_runs": "At minute 0 past hour 9 through 17 on Monday through Friday",
                    "use_cases": ["Active monitoring", "Business hour notifications"]
                },
                "quarterly": {
                    "expression": "0 9 1 1,4,7,10 *",
                    "description": "Run quarterly on the 1st at 9 AM (Jan, Apr, Jul, Oct)",
                    "next_runs": "At 09:00 on day-of-month 1 in January, April, July, and October",
                    "use_cases": ["Quarterly reports", "Seasonal tasks"]
                },
                "yearly": {
                    "expression": "0 9 1 1 *",
                    "description": "Run yearly on January 1st at 9 AM",
                    "next_runs": "At 09:00 on January 1",
                    "use_cases": ["Annual reports", "Yearly maintenance", "License renewals"]
                }
            },
            "api_monitoring": {
                "high_frequency": {
                    "expression": "*/2 * * * *",
                    "description": "Monitor API every 2 minutes",
                    "next_runs": "At minute 0, 2, 4, 6, etc.",
                    "use_cases": ["Critical API monitoring", "High availability checks"]
                },
                "standard_monitoring": {
                    "expression": "*/5 * * * *",
                    "description": "Monitor API every 5 minutes",
                    "next_runs": "At minute 0, 5, 10, 15, etc.",
                    "use_cases": ["Standard API health checks", "Service monitoring"]
                },
                "light_monitoring": {
                    "expression": "*/15 * * * *",
                    "description": "Monitor API every 15 minutes",
                    "next_runs": "At minute 0, 15, 30, 45",
                    "use_cases": ["Light monitoring", "Non-critical services"]
                }
            },
            "backup_schedules": {
                "daily_backup": {
                    "expression": "0 2 * * *",
                    "description": "Daily backup at 2 AM",
                    "next_runs": "At 02:00 every day",
                    "use_cases": ["Database backups", "File system backups"]
                },
                "weekly_backup": {
                    "expression": "0 3 * * 0",
                    "description": "Weekly backup every Sunday at 3 AM",
                    "next_runs": "At 03:00 on Sunday",
                    "use_cases": ["Full system backups", "Weekly archives"]
                },
                "incremental_backup": {
                    "expression": "0 1 * * *",
                    "description": "Incremental backup daily at 1 AM",
                    "next_runs": "At 01:00 every day",
                    "use_cases": ["Incremental backups", "Change-only backups"]
                }
            }
        }

    def get_templates_resource(self) -> Dict[str, Any]:
        """Get the cron templates resource content."""
        logger.debug("Generating cron templates resource")

        # Count total templates
        total_templates = sum(len(category) for category in self._templates.values())

        return {
            "uri": self.base_uri,
            "mimeType": "application/json",
            "text": json.dumps({
                "meta": {
                    "description": "Comprehensive collection of cron expression templates and patterns",
                    "total_templates": total_templates,
                    "categories": list(self._templates.keys()),
                    "format": "5-field cron expressions (minute hour day month day-of-week)",
                    "usage": "Copy the 'expression' field to use in job creation"
                },
                "syntax_guide": {
                    "fields": [
                        "minute (0-59)",
                        "hour (0-23)",
                        "day of month (1-31)",
                        "month (1-12)",
                        "day of week (0-6, Sunday=0)"
                    ],
                    "special_characters": {
                        "*": "Any value (wildcard)",
                        "*/n": "Every n units (e.g., */5 = every 5)",
                        "n-m": "Range from n to m (e.g., 1-5)",
                        "n,m": "List of values (e.g., 1,3,5)",
                        "n/m": "Every m starting at n"
                    },
                    "examples": {
                        "*/15 * * * *": "Every 15 minutes",
                        "0 9-17 * * 1-5": "Every hour from 9 AM to 5 PM, Monday to Friday",
                        "30 14 * * 0": "2:30 PM every Sunday"
                    }
                },
                "templates": self._templates,
                "validation_tips": [
                    "Use online cron validators to test expressions",
                    "Remember: Sunday = 0, Monday = 1, etc.",
                    "Month values: January = 1, December = 12",
                    "Consider timezone when scheduling",
                    "Test with frequent patterns first, then adjust timing"
                ],
                "resource_info": {
                    "last_updated": "static",
                    "type": "cron_templates",
                    "refresh_rate": "static"
                }
            }, indent=2)
        }


# Export the provider class
__all__ = ["CronTemplatesProvider"]