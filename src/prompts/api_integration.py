"""API integration prompts for the Cronlytic MCP Server."""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class APIIntegrationPrompts:
    """Interactive prompts for API integration workflows."""

    @staticmethod
    def get_prompts() -> List[Dict[str, Any]]:
        """Get all API integration prompts."""
        return [
            SETUP_CONFIGURATION_PROMPT,
            AUTHENTICATION_GUIDE_PROMPT,
            CLAUDE_DESKTOP_INTEGRATION_PROMPT,
            WEBHOOK_TESTING_GUIDE_PROMPT,
            API_TROUBLESHOOTING_PROMPT
        ]


# Setup Configuration Prompt
SETUP_CONFIGURATION_PROMPT = {
    "name": "setup_configuration",
    "description": "Complete setup guide for Cronlytic MCP server configuration",
    "arguments": [
        {
            "name": "setup_stage",
            "description": "Current setup stage or area needing help",
            "required": False
        },
        {
            "name": "environment",
            "description": "Target environment (development, staging, production)",
            "required": False
        }
    ],
    "template": """# Cronlytic MCP Server Setup Guide

I'll guide you through setting up the Cronlytic MCP server from start to finish.

## 🚀 Setup Overview

**Current Stage:** {setup_stage}
**Environment:** {environment}

### Prerequisites Checklist
- ✅ Python 3.8+ installed
- ✅ pip package manager available
- ✅ Cronlytic account with API access
- ✅ Claude Desktop installed (for MCP integration)

## Step 1: Installation

### Install the MCP Server
```bash
# Install from source
git clone https://github.com/Cronlytic/cronlytic-mcp-server
cd cronlytic-mcp-server
pip install -e .

# Or install from PyPI (when available)
pip install cronlytic-mcp-server
```

### Verify Installation
```bash
python -c "import cronlytic_mcp_server; print('Installation successful!')"
```

## Step 2: Authentication Setup

### Get Your API Credentials
1. **Log into Cronlytic Dashboard**: Visit https://app.cronlytic.com
2. **Navigate to API Settings**: Settings → API Keys
3. **Generate API Key**: Create a new API key for MCP integration
4. **Copy User ID**: Found in your account settings

### Configure Credentials

**Option A: Environment Variables (Recommended)**
```bash
export CRONLYTIC_API_KEY="your-api-key-here"
export CRONLYTIC_USER_ID="your-user-id-here"
export CRONLYTIC_BASE_URL="https://api.cronlytic.com/prog"
```

**Option B: Configuration File**
```json
{
  "api_key": "your-api-key-here",
  "user_id": "your-user-id-here",
  "base_url": "https://api.cronlytic.com/prog",
  "timeout": 30,
  "max_retries": 3
}
```

## Step 3: Test Connection

### Basic Health Check
```bash
# Test API connectivity
python -c "
from cronlytic_mcp_server.utils.auth import get_auth_config
from cronlytic_mcp_server.tools.health_check import health_check_tool
import asyncio

async def test():
    config = get_auth_config()
    result = await health_check_tool(config)
    print(f'Status: {result[\"status\"]}')

asyncio.run(test())
"
```

## Step 4: Claude Desktop Integration

### Add to Claude Desktop Configuration
Edit your Claude Desktop configuration file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows:** `%APPDATA%\\Claude\\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python",
      "args": ["-m", "cronlytic_mcp_server"],
      "env": {
        "CRONLYTIC_API_KEY": "your-api-key-here",
        "CRONLYTIC_USER_ID": "your-user-id-here"
      }
    }
  }
}
```

## Step 5: Verification & Testing

### Test MCP Integration
1. **Restart Claude Desktop**
2. **Open new conversation**
3. **Test basic commands:**
   - "Check my Cronlytic job health"
   - "List all my cron jobs"
   - "Create a simple monitoring job"

### Verify All Features
- ✅ Tools: Job creation, listing, updates
- ✅ Resources: Job data, cron templates
- ✅ Prompts: Interactive workflows

**Need help with a specific step?** Tell me where you're stuck and I'll provide detailed assistance.
"""
}

# Authentication Guide Prompt
AUTHENTICATION_GUIDE_PROMPT = {
    "name": "authentication_guide",
    "description": "Comprehensive guide for authentication setup and troubleshooting",
    "arguments": [
        {
            "name": "auth_issue",
            "description": "Specific authentication issue or setup question",
            "required": False
        }
    ],
    "template": """# Authentication Setup & Troubleshooting

I'll help you configure and troubleshoot authentication for the Cronlytic MCP server.

## 🔐 Authentication Overview

**Current Issue:** {auth_issue}

### Required Credentials
- **API Key**: Your unique authentication token
- **User ID**: Your Cronlytic account identifier
- **Base URL**: API endpoint (usually https://api.cronlytic.com/prog)

## 🗝️ Getting Your Credentials

### Step 1: Access Cronlytic Dashboard
1. Visit **https://app.cronlytic.com**
2. Log in with your account credentials
3. Navigate to **Settings** → **API Keys**

### Step 2: Generate API Key
1. Click **"Generate New API Key"**
2. Give it a descriptive name (e.g., "MCP Server")
3. **Copy the key immediately** (it won't be shown again)
4. Store it securely

### Step 3: Find Your User ID
1. Go to **Account Settings**
2. Copy your **User ID** (usually a UUID format)

## 🔧 Configuration Methods

### Method 1: Environment Variables (Recommended)

**Linux/macOS:**
```bash
export CRONLYTIC_API_KEY="ck_live_1234567890abcdef"
export CRONLYTIC_USER_ID="12345678-1234-1234-1234-123456789abc"
export CRONLYTIC_BASE_URL="https://api.cronlytic.com/prog"
```

**Windows:**
```cmd
set CRONLYTIC_API_KEY=ck_live_1234567890abcdef
set CRONLYTIC_USER_ID=12345678-1234-1234-1234-123456789abc
set CRONLYTIC_BASE_URL=https://api.cronlytic.com/prog
```

### Method 2: Configuration File

Create `config/auth.json`:
```json
{
  "api_key": "ck_live_1234567890abcdef",
  "user_id": "12345678-1234-1234-1234-123456789abc",
  "base_url": "https://api.cronlytic.com/prog",
  "timeout": 30,
  "max_retries": 3
}
```

**Need specific help?** Tell me about your authentication issue and I'll provide targeted troubleshooting steps.
"""
}

# Claude Desktop Integration Prompt
CLAUDE_DESKTOP_INTEGRATION_PROMPT = {
    "name": "claude_desktop_integration",
    "description": "Step-by-step guide for integrating with Claude Desktop",
    "arguments": [
        {
            "name": "integration_step",
            "description": "Current integration step or issue",
            "required": False
        },
        {
            "name": "operating_system",
            "description": "Operating system (macOS, Windows, Linux)",
            "required": False
        }
    ],
    "template": """# Claude Desktop Integration Guide

I'll help you integrate the Cronlytic MCP server with Claude Desktop for seamless cron job management.

## 🖥️ Platform-Specific Setup

**Operating System:** {operating_system}
**Current Step:** {integration_step}

### Configuration File Locations

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\\Claude\\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

## 📝 Configuration Setup

### Basic Configuration
```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python",
      "args": ["-m", "cronlytic_mcp_server"],
      "env": {
        "CRONLYTIC_API_KEY": "your-api-key-here",
        "CRONLYTIC_USER_ID": "your-user-id-here"
      }
    }
  }
}
```

### Advanced Configuration
```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python",
      "args": ["-m", "cronlytic_mcp_server"],
      "env": {
        "CRONLYTIC_API_KEY": "your-api-key-here",
        "CRONLYTIC_USER_ID": "your-user-id-here",
        "CRONLYTIC_BASE_URL": "https://api.cronlytic.com/prog",
        "CRONLYTIC_TIMEOUT": "30",
        "CRONLYTIC_MAX_RETRIES": "3",
        "CRONLYTIC_LOG_LEVEL": "INFO"
      },
      "timeout": 60
    }
  }
}
```

## 🔧 Installation Steps

### Step 1: Install MCP Server
```bash
# Install the Cronlytic MCP server
pip install cronlytic-mcp-server

# Verify installation
python -m cronlytic_mcp_server --version
```

### Step 2: Create Configuration
1. **Locate configuration file** (see paths above)
2. **Create directory** if it doesn't exist
3. **Add configuration** with your credentials
4. **Validate JSON syntax**

### Step 3: Restart Claude Desktop
1. **Quit Claude Desktop** completely
2. **Wait 5 seconds**
3. **Restart Claude Desktop**
4. **Open new conversation**

### Step 4: Test Integration
Try these commands in Claude:
- "Check my Cronlytic health"
- "List my cron jobs"
- "Show me available cron templates"

**Ready for next steps?** Tell me about your current progress and any issues you're encountering.
"""
}

# Webhook Testing Guide Prompt
WEBHOOK_TESTING_GUIDE_PROMPT = {
    "name": "webhook_testing_guide",
    "description": "Comprehensive guide for testing webhooks and endpoints",
    "arguments": [
        {
            "name": "webhook_url",
            "description": "The webhook URL to test",
            "required": False
        },
        {
            "name": "http_method",
            "description": "HTTP method for the webhook (GET, POST, PUT, DELETE)",
            "required": False
        },
        {
            "name": "test_type",
            "description": "Type of testing to perform (basic, comprehensive, load)",
            "required": False
        }
    ],
    "template": """# Webhook Testing Guide

I'll help you thoroughly test your webhook endpoints to ensure reliable cron job execution.

## 🔗 Webhook Overview

**Target URL:** {webhook_url}
**HTTP Method:** {http_method}

### Testing Strategy
Before creating a cron job, it's crucial to validate that your webhook endpoint is working correctly.

## 🧪 Testing Steps

### Step 1: Basic Connectivity Test
```bash
# Test basic connectivity
curl -I {webhook_url}

# Expected: HTTP 200-299 status code
# Check for proper headers and response
```

### Step 2: Method-Specific Testing

**GET Request Testing:**
```bash
curl -X GET "{webhook_url}" -v
```

**POST Request Testing:**
```bash
curl -X POST "{webhook_url}" \\
  -H "Content-Type: application/json" \\
  -d '{"test": "data", "timestamp": "2024-01-01T00:00:00Z"}' \\
  -v
```

**Authentication Testing (if required):**
```bash
curl -X {http_method} "{webhook_url}" \\
  -H "Authorization: Bearer YOUR_TOKEN" \\
  -H "X-API-Key: YOUR_API_KEY" \\
  -v
```

### Step 3: Response Validation
✅ **Status Code**: Should be 200-299
✅ **Response Time**: Should be < 30 seconds
✅ **Content Type**: Should match expected format
✅ **Response Body**: Should contain expected data

### Step 4: Error Handling Test
```bash
# Test with invalid data
curl -X {http_method} "{webhook_url}" \\
  -H "Content-Type: application/json" \\
  -d '{"invalid": "data"}' \\
  -v

# Test with missing headers
curl -X {http_method} "{webhook_url}" -v
```

## 🔍 Advanced Testing

### Load Testing
```bash
# Simple load test (10 concurrent requests)
for i in {{1..10}}; do
  curl -X {http_method} "{webhook_url}" &
done
wait
```

### Timeout Testing
```bash
# Test with custom timeout
curl -X {http_method} "{webhook_url}" --max-time 30 -v
```

### SSL/TLS Validation
```bash
# Test SSL certificate
curl -X {http_method} "{webhook_url}" --ssl-reqd -v

# Check certificate details
openssl s_client -connect $(echo {webhook_url} | cut -d'/' -f3):443
```

## 📊 Common Response Patterns

### Successful Responses
- **200 OK**: Standard success
- **201 Created**: Resource created
- **202 Accepted**: Request accepted for processing
- **204 No Content**: Success with no response body

### Error Responses to Fix
- **400 Bad Request**: Check request format
- **401 Unauthorized**: Verify authentication
- **403 Forbidden**: Check permissions
- **404 Not Found**: Verify URL
- **422 Unprocessable Entity**: Validate request data
- **500 Internal Server Error**: Contact endpoint owner

**Ready to test your webhook?** Provide the URL and method, and I'll guide you through comprehensive testing to ensure reliable cron job execution.
"""
}

# API Troubleshooting Prompt
API_TROUBLESHOOTING_PROMPT = {
    "name": "api_troubleshooting_guide",
    "description": "Comprehensive API and integration troubleshooting assistance",
    "arguments": [
        {
            "name": "problem_type",
            "description": "Type of API or integration problem",
            "required": False
        },
        {
            "name": "error_message",
            "description": "Specific error message or symptom",
            "required": False
        }
    ],
    "template": """# API & Integration Troubleshooting

I'll help you diagnose and resolve API connectivity, authentication, and integration issues.

## 🔍 Problem Identification

**Problem Type:** {problem_type}
**Error Message:** {error_message}

### Common Problem Categories

**🔌 Connection Issues**
- Cannot reach API endpoints
- Timeout errors
- Network connectivity problems
- DNS resolution failures

**🔐 Authentication Problems**
- Invalid API keys or tokens
- Expired credentials
- Wrong authentication method
- Permission/authorization errors

**⚙️ Configuration Issues**
- Incorrect MCP server setup
- Wrong environment variables
- Claude Desktop integration problems
- Invalid JSON configuration

**📊 Performance Issues**
- Slow response times
- Rate limiting
- High error rates
- Resource constraints

## 🛠️ Diagnostic Steps

### Step 1: Basic Connectivity
```bash
# Test internet connectivity
ping google.com

# Test Cronlytic API connectivity
curl https://api.cronlytic.com/prog/ping

# Check DNS resolution
nslookup api.cronlytic.com
```

### Step 2: Authentication Verification
```bash
# Check environment variables
echo $CRONLYTIC_API_KEY
echo $CRONLYTIC_USER_ID

# Test API authentication
curl -H "Authorization: Bearer $CRONLYTIC_API_KEY" \\
     -H "X-User-ID: $CRONLYTIC_USER_ID" \\
     https://api.cronlytic.com/prog/jobs
```

### Step 3: Configuration Validation
```python
# Validate MCP configuration
import json
from pathlib import Path

# Check Claude Desktop config
config_path = Path.home() / "Library/Application Support/Claude/claude_desktop_config.json"
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
        print(json.dumps(config, indent=2))
else:
    print("Claude Desktop config not found")
```

## 🚨 Common Issues & Solutions

### "Authentication failed (401)"
**Cause:** Invalid or expired credentials
**Solutions:**
1. **Verify API key format**: Should start with `ck_`
2. **Check User ID format**: Should be a UUID
3. **Regenerate credentials** if necessary
4. **Test with curl**:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \\
     -H "X-User-ID: YOUR_USER_ID" \\
     https://api.cronlytic.com/prog/jobs
```

### "Connection timeout"
**Cause:** Network or firewall issues
**Solutions:**
```bash
# Test direct connectivity
telnet api.cronlytic.com 443

# Check for proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test with different timeout
curl --timeout 60 https://api.cronlytic.com/prog/ping
```

### "MCP server not responding"
**Cause:** Server startup or configuration issues
**Solutions:**
1. **Check Claude Desktop logs**
2. **Restart Claude Desktop**
3. **Verify configuration syntax**
4. **Test server manually**:
```bash
python -m cronlytic_mcp_server --test
```

**Need immediate help?** Describe your specific issue and any error messages you're seeing, and I'll provide targeted troubleshooting steps.
"""
}