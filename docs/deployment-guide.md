# Cronlytic MCP Server Deployment Guide

This guide provides comprehensive instructions for deploying and configuring the Cronlytic MCP Server in various environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation Methods](#installation-methods)
3. [Configuration](#configuration)
4. [Claude Desktop Integration](#claude-desktop-integration)
5. [Environment-Specific Deployments](#environment-specific-deployments)
6. [Security Considerations](#security-considerations)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Linux, macOS, or Windows
- **Memory**: Minimum 512MB RAM
- **Disk Space**: 100MB for installation
- **Network**: Internet connectivity for Cronlytic API access

### Required Credentials

Before deployment, obtain your Cronlytic API credentials:

1. Sign up at [Cronlytic](https://cronlytic.com)
2. Navigate to API Keys section
3. Generate a new API key
4. Note your User ID and API Key

## Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
# Clone the repository
git clone https://github.com/Cronlytic/cronlytic-mcp-server.git
cd cronlytic-mcp-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests to verify installation
python3 -m pytest tests/ -v
```

### Method 2: Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Set environment variables
ENV PYTHONPATH=/app/src
ENV CRONLYTIC_CONFIG_FILE=/app/config/cronlytic_config.json

# Run the server
CMD ["python3", "-m", "src.server"]
```

## Configuration

### Environment Variables

The server supports configuration through environment variables:

```bash
# Required
export CRONLYTIC_API_KEY="your_api_key"
export CRONLYTIC_USER_ID="your_user_id"

# Optional
export CRONLYTIC_BASE_URL="https://api.cronlytic.com/prog"
export CRONLYTIC_TIMEOUT="30"
export CRONLYTIC_MAX_RETRIES="3"
```

### Configuration File

Create `cronlytic_config.json`:

```json
{
    "api_key": "your_api_key_here",
    "user_id": "your_user_id_here",
    "base_url": "https://api.cronlytic.com/prog",
    "timeout": 30,
    "max_retries": 3,
    "retry_delay": 1.0
}
```

## Claude Desktop Integration

### Windows Configuration

Edit Claude Desktop config file at:
`%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "cronlytic": {
      "command": "python",
      "args": [
        "C:\\path\\to\\cronlytic-mcp-server\\src\\server.py"
      ],
      "env": {
        "CRONLYTIC_API_KEY": "your_api_key",
        "CRONLYTIC_USER_ID": "your_user_id"
      }
    }
  }
}
```

### macOS Configuration

Edit Claude Desktop config file at:
`~/Library/Application Support/Claude/claude_desktop_config.json`

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
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    }
  }
}
```

### Linux Configuration

Edit Claude Desktop config file at:
`~/.config/claude/claude_desktop_config.json`

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
        "PYTHONPATH": "/path/to/cronlytic-mcp-server/src"
      }
    }
  }
}
```

## Security Considerations

### API Key Management

1. **Never commit API keys to version control**
2. **Use environment variables or secret management systems**
3. **Rotate API keys regularly**
4. **Implement least privilege access**

### File Permissions

```bash
# Secure configuration files
sudo chmod 600 /etc/cronlytic/config.json
sudo chown cronlytic:cronlytic /etc/cronlytic/config.json

# Secure application directory
sudo chmod 755 /opt/cronlytic-mcp-server
sudo chown -R cronlytic:cronlytic /opt/cronlytic-mcp-server
```

## Monitoring and Maintenance

### Health Checks

```bash
# Simple health check script
#!/bin/bash
cd /opt/cronlytic-mcp-server
source venv/bin/activate

python3 -c "
import asyncio
from src.utils.auth import get_auth_config
from src.cronlytic_client import CronlyticAPIClient

async def health_check():
    config = get_auth_config()
    async with CronlyticAPIClient(config) as client:
        result = await client.ping()
        print('Health check passed:', result)

asyncio.run(health_check())
"
```

## Troubleshooting

### Common Issues

#### Authentication Errors

```bash
# Check API credentials
python3 -c "
from src.utils.auth import get_auth_config
config = get_auth_config()
print(f'API Key: {config.api_key[:8]}...')
print(f'User ID: {config.user_id}')
"

# Test API connectivity
curl -X GET "https://api.cronlytic.com/prog/ping" \
  -H "X-API-Key: your_api_key" \
  -H "X-User-ID: your_user_id"
```

#### Connection Issues

```bash
# Check network connectivity
ping api.cronlytic.com

# Test with verbose curl
curl -v "https://api.cronlytic.com/prog/ping"
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python3 -m src.server --debug
```

## Support and Maintenance

### Regular Maintenance Tasks

1. **Weekly**: Review logs for errors and performance issues
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and rotate API keys

### Getting Support

- **Documentation**: Check this guide and API documentation
- **Logs**: Include relevant log files with support requests
- **Environment**: Provide system information and configuration details