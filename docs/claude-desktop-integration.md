# Claude Desktop Integration Guide

This guide provides detailed instructions for integrating the Cronlytic MCP Server with Claude Desktop, enabling seamless cron job management through Claude's interface.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Overview](#installation-overview)
3. [Platform-Specific Setup](#platform-specific-setup)
4. [Configuration](#configuration)
5. [Testing the Integration](#testing-the-integration)
6. [Usage Examples](#usage-examples)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Configuration](#advanced-configuration)

## Prerequisites

### Claude Desktop Requirements

- **Claude Desktop**: Version 1.0 or higher
- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher installed and accessible

### Cronlytic MCP Server Requirements

- ✅ Cronlytic MCP Server installed and tested
- ✅ Valid Cronlytic API credentials (API key and User ID)
- ✅ Network connectivity to api.cronlytic.com

### Verify Prerequisites

Before proceeding, ensure all components are working:

```bash
# 1. Check Python installation
python3 --version
# Should output: Python 3.8.x or higher

# 2. Verify Cronlytic MCP Server
cd /path/to/cronlytic-mcp-server
source .venv/bin/activate  # Activate virtual environment
python3 -m pytest tests/ -v
# Should show: 88 passed

# 3. Test API connectivity
python3 -c "
import asyncio
from src.utils.auth import get_auth_config
from src.cronlytic_client import CronlyticAPIClient

async def test():
    config = get_auth_config()
    async with CronlyticAPIClient(config) as client:
        result = await client.ping()
        print('✅ API connectivity verified:', result)

asyncio.run(test())
"
```

## Installation Overview

The integration process involves:

1. **Locating** Claude Desktop's configuration file
2. **Configuring** the MCP server connection
3. **Setting** environment variables for authentication
4. **Testing** the integration
5. **Verifying** all tools and prompts are available

## Platform-Specific Setup

### Windows Configuration

#### Step 1: Locate Configuration File

Claude Desktop configuration is stored at:
```
%APPDATA%\Claude\claude_desktop_config.json
```

To find this path:
1. Press `Win + R`, type `%APPDATA%`, press Enter
2. Navigate to `Claude` folder
3. Look for `claude_desktop_config.json`

#### Step 2: Configure MCP Server

Edit or create `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python",
      "args": [
        "C:\\path\\to\\cronlytic-mcp-server\\src\\server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key_here",
        "CRONLYTIC_USER_ID": "your_user_id_here",
        "PYTHONPATH": "C:\\path\\to\\cronlytic-mcp-server\\src"
      }
    }
  }
}
```

#### Step 3: Windows-Specific Notes

- Use **forward slashes** (`/`) or **double backslashes** (`\\`) in paths
- Ensure Python is in your PATH or use full path: `"C:\\Python39\\python.exe"`
- For virtual environments, use: `"C:\\path\\to\\cronlytic-mcp-server\\.venv\\Scripts\\python.exe"`

### macOS Configuration

#### Step 1: Locate Configuration File

Claude Desktop configuration is stored at:
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

To access this location:
1. Open Finder
2. Press `Cmd + Shift + G`
3. Type: `~/Library/Application Support/Claude/`
4. Look for `claude_desktop_config.json`

#### Step 2: Configure MCP Server

Edit or create `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python3",
      "args": [
        "/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key_here",
        "CRONLYTIC_USER_ID": "your_user_id_here",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    }
  }
}
```

#### Step 3: macOS-Specific Notes

- Use `python3` instead of `python`
- For Homebrew Python: `"/opt/homebrew/bin/python3"`
- For virtual environments: `"/path/to/cronlytic-mcp-server/.venv/bin/python"`

### Linux Configuration

#### Step 1: Locate Configuration File

Claude Desktop configuration is stored at:
```
~/.config/claude/claude_desktop_config.json
```

Create the directory if it doesn't exist:
```bash
mkdir -p ~/.config/claude
```

#### Step 2: Configure MCP Server

Edit or create `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python3",
      "args": [
        "/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key_here",
        "CRONLYTIC_USER_ID": "your_user_id_here",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    }
  }
}
```

#### Step 3: Linux-Specific Notes

- Ensure the configuration file has proper permissions: `chmod 644 ~/.config/claude/claude_desktop_config.json`
- For system-wide installation: Use full paths like `/opt/cronlytic-mcp-server/`

## Configuration

### Complete Configuration Template

Here's a comprehensive configuration template with all options:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python3",
      "args": [
        "/absolute/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key_here",
        "CRONLYTIC_USER_ID": "your_user_id_here",
        "CRONLYTIC_BASE_URL": "https://api.cronlytic.com/prog",
        "CRONLYTIC_TIMEOUT": "30",
        "CRONLYTIC_MAX_RETRIES": "3",
        "PYTHONPATH": "/absolute/path/to/cronlytic-mcp-server/src",
        "LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### Environment Variables Explained

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CRONLYTIC_API_KEY` | ✅ Yes | None | Your Cronlytic API key |
| `CRONLYTIC_USER_ID` | ✅ Yes | None | Your Cronlytic User ID |
| `CRONLYTIC_BASE_URL` | ❌ No | `https://api.cronlytic.com/prog` | Cronlytic API base URL |
| `CRONLYTIC_TIMEOUT` | ❌ No | `30` | Request timeout in seconds |
| `CRONLYTIC_MAX_RETRIES` | ❌ No | `3` | Maximum retry attempts |
| `PYTHONPATH` | ✅ Yes | None | Path to server source code |
| `LOG_LEVEL` | ❌ No | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |

### Alternative Configuration Methods

#### Method 1: Configuration File

Instead of environment variables, you can use a configuration file:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python3",
      "args": [
        "/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_CONFIG_FILE": "/path/to/cronlytic_config.json",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    }
  }
}
```

Create `/path/to/cronlytic_config.json`:
```json
{
    "api_key": "your_api_key_here",
    "user_id": "your_user_id_here",
    "base_url": "https://api.cronlytic.com/prog",
    "timeout": 30,
    "max_retries": 3
}
```

#### Method 2: Virtual Environment

For isolated Python environments:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "/path/to/cronlytic-mcp-server/.venv/bin/python",
      "args": [
        "/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key_here",
        "CRONLYTIC_USER_ID": "your_user_id_here"
      }
    }
  }
}
```

## Testing the Integration

### Step 1: Restart Claude Desktop

After updating the configuration:

1. **Completely close** Claude Desktop
2. **Wait 5 seconds**
3. **Restart** Claude Desktop
4. **Wait for initialization** (may take 10-30 seconds)

### Step 2: Verify Connection

In Claude Desktop, try these test commands:

#### Test 1: Health Check
```
Can you check if the Cronlytic MCP server is connected and working?
```

Expected response should mention the health check tool and API connectivity.

#### Test 2: List Available Tools
```
What Cronlytic tools are available to me?
```

You should see:
- ✅ `health_check` - Test API connectivity
- ✅ `create_job` - Create new cron jobs
- ✅ `list_jobs` - List existing jobs
- ✅ `get_job` - Get job details
- ✅ `update_job` - Update job configuration
- ✅ `delete_job` - Delete jobs
- ✅ `pause_job` - Pause job execution
- ✅ `resume_job` - Resume paused jobs
- ✅ `get_job_logs` - View execution logs

#### Test 3: List Available Prompts
```
What Cronlytic prompts can you help me with?
```

You should see 18 prompts across 4 categories:
- **Job Management** (5 prompts)
- **API Integration** (5 prompts)
- **Troubleshooting** (4 prompts)
- **Workflow Optimization** (4 prompts)

### Step 3: Functional Test

Try creating a simple test job:

```
I want to create a simple health check job that calls https://httpbin.org/get every hour. Can you help me set this up?
```

Claude should:
1. Use the `create_job_flow` prompt to guide you
2. Create the job using the `create_job` tool
3. Show you the job details and next execution time

## Usage Examples

### Example 1: Create a Daily Backup Job

```
User: I need to set up a daily backup job that calls my backup API at 2 AM every day.

Claude: I'll help you create a daily backup job. Let me use the job creation flow to guide you through this.

[Claude uses create_job_flow prompt and create_job tool]

The backup job has been created successfully! Here are the details:
- Job Name: daily-backup
- URL: https://your-api.com/backup
- Schedule: Every day at 2:00 AM
- Next Execution: Tomorrow at 2:00 AM
- Job ID: abc123-def456

Would you like me to show you how to monitor this job or set up notifications?
```

### Example 2: Monitor Existing Jobs

```
User: Can you show me all my current cron jobs and their status?

Claude: I'll retrieve all your current cron jobs for you.

[Claude uses list_jobs tool]

Here are your current cron jobs:

1. **daily-backup** (ID: abc123)
   - Status: Pending
   - Schedule: Daily at 2:00 AM
   - Last Run: Yesterday at 2:00 AM (Success)
   - Next Run: Tomorrow at 2:00 AM

2. **health-check** (ID: def456)
   - Status: Pending
   - Schedule: Every 5 minutes
   - Last Run: 3 minutes ago (Success)
   - Next Run: In 2 minutes

Would you like me to get detailed logs for any specific job?
```

### Example 3: Troubleshoot a Failed Job

```
User: My backup job is failing. Can you help me troubleshoot it?

Claude: I'll help you troubleshoot the backup job. Let me check its recent execution logs.

[Claude uses get_job_logs tool and troubleshooting_guide prompt]

I found the issue! Looking at the logs, your backup job is failing with a 401 authentication error. Here's what I recommend:

1. **Check API Token**: Your authentication token may have expired
2. **Verify Endpoint**: Ensure https://your-api.com/backup is accessible
3. **Update Headers**: You may need to refresh the Authorization header

Would you like me to help you update the job with new credentials?
```

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: "MCP Server Not Found"

**Symptoms**: Claude Desktop doesn't recognize the Cronlytic server

**Solutions**:
1. **Check file paths**: Ensure all paths in the config are absolute and correct
2. **Verify Python path**: Test the command manually:
   ```bash
   python3 /path/to/cronlytic-mcp-server/src/server.py
   ```
3. **Check permissions**: Ensure Claude Desktop can access the files
4. **Restart Claude Desktop**: Completely close and reopen

#### Issue 2: "Authentication Failed"

**Symptoms**: Server connects but API calls fail

**Solutions**:
1. **Verify credentials**: Check your API key and User ID
2. **Test manually**:
   ```bash
   curl -X GET "https://api.cronlytic.com/prog/ping" \
     -H "X-API-Key: your_api_key" \
     -H "X-User-ID: your_user_id"
   ```
3. **Check environment variables**: Ensure they're properly set in the config

#### Issue 3: "Import Errors"

**Symptoms**: Python module import failures

**Solutions**:
1. **Check PYTHONPATH**: Ensure it points to the `src` directory
2. **Install dependencies**:
   ```bash
   cd /path/to/cronlytic-mcp-server
   pip install -r requirements.txt
   ```
3. **Use virtual environment**: Point to the venv Python executable

#### Issue 4: "Connection Timeout"

**Symptoms**: Server starts but operations time out

**Solutions**:
1. **Check network connectivity**: Ensure internet access
2. **Increase timeout**:
   ```json
   "env": {
     "CRONLYTIC_TIMEOUT": "60"
   }
   ```
3. **Check firewall settings**: Ensure HTTPS traffic is allowed

### Debug Mode

Enable detailed logging for troubleshooting:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python3",
      "args": [
        "/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key",
        "CRONLYTIC_USER_ID": "your_user_id",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src",
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```

### Manual Testing

Test the server independently:

```bash
# Navigate to project directory
cd /path/to/cronlytic-mcp-server

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export CRONLYTIC_API_KEY="your_api_key"
export CRONLYTIC_USER_ID="your_user_id"

# Test server directly
python3 src/server.py

# In another terminal, test with MCP Inspector
npm install -g @modelcontextprotocol/inspector
mcp-inspector python3 /path/to/cronlytic-mcp-server/src/server.py
```

## Advanced Configuration

### Production Configuration

For production environments:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "/usr/bin/python3",
      "args": [
        "/opt/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_CONFIG_FILE": "/etc/cronlytic/config.json",
        "PYTHONPATH": "/opt/cronlytic-mcp-server/src",
        "LOG_LEVEL": "INFO"
      },
      "timeout": 30,
      "cwd": "/opt/cronlytic-mcp-server"
    }
  }
}
```

### Multiple Environments

Configure different environments:

```json
{
  "mcpServers": {
    "cronlytic-dev": {
      "command": "python3",
      "args": ["/path/to/cronlytic-mcp-server/src/server.py"],
      "env": {
        "CRONLYTIC_API_KEY": "dev_api_key",
        "CRONLYTIC_USER_ID": "dev_user_id",
        "CRONLYTIC_BASE_URL": "https://dev-api.cronlytic.com/prog",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    },
    "cronlytic-prod": {
      "command": "python3",
      "args": ["/path/to/cronlytic-mcp-server/src/server.py"],
      "env": {
        "CRONLYTIC_API_KEY": "prod_api_key",
        "CRONLYTIC_USER_ID": "prod_user_id",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    }
  }
}
```

### Security Best Practices

1. **Secure Configuration File**:
   ```bash
   # Set appropriate permissions
   chmod 600 ~/.config/claude/claude_desktop_config.json
   ```

2. **Use Configuration Files Instead of Environment Variables**:
   - Store sensitive data in separate config files
   - Use proper file permissions (600)
   - Keep config files out of version control

3. **Regular Updates**:
   - Keep the MCP server updated
   - Rotate API keys periodically
   - Monitor for security updates

### Performance Optimization

For optimal performance:

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python3",
      "args": [
        "/path/to/cronlytic-mcp-server/src/server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key",
        "CRONLYTIC_USER_ID": "your_user_id",
        "CRONLYTIC_TIMEOUT": "15",
        "CRONLYTIC_MAX_RETRIES": "2",
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      },
      "timeout": 30
    }
  }
}
```

## Support

If you encounter issues not covered in this guide:

1. **Check Logs**: Look for error messages in Claude Desktop logs
2. **Test Manually**: Run the server independently to isolate issues
3. **Verify Setup**: Ensure all prerequisites are met
4. **Update Components**: Ensure you're using the latest versions

For additional support, refer to:
- [Deployment Guide](deployment-guide.md)
- [Example Workflows](example-workflows.md)
- [Cronlytic API Documentation](cronlytic-API-specification.md)

This integration guide should help you successfully set up and use the Cronlytic MCP Server with Claude Desktop across all supported platforms.