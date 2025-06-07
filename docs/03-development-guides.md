# Development Guides

This document provides comprehensive guides for developing with the Model Context Protocol (MCP), covering both client and server development, debugging, and best practices.

## Introduction

MCP (Model Context Protocol) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to connect LLMs with the context they need.

## For Client Developers

### Getting Started

Client applications in MCP act as the host for language models and manage connections to MCP servers. They present server capabilities to users and handle the interaction flow.

### Key Responsibilities

1. **Server Management**: Connect to and manage MCP servers
2. **User Interface**: Present prompts, tools, and resources to users
3. **Model Integration**: Facilitate communication between servers and language models
4. **Security**: Implement appropriate safeguards and user controls

### Basic Client Implementation

```python
from mcp import Client
import asyncio

async def main():
    # Create client instance
    client = Client()

    # Connect to a server
    await client.connect("stdio", {
        "command": "python",
        "args": ["server.py"]
    })

    # List available tools
    tools = await client.list_tools()
    print(f"Available tools: {[tool.name for tool in tools]}")

    # List available resources
    resources = await client.list_resources()
    print(f"Available resources: {[resource.name for resource in resources]}")

    # Call a tool
    result = await client.call_tool("example_tool", {"param": "value"})
    print(f"Tool result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
```

### Transport Implementation

#### Stdio Transport

```python
class StdioTransport:
    def __init__(self, command, args=None):
        self.command = command
        self.args = args or []
        self.process = None

    async def connect(self):
        self.process = await asyncio.create_subprocess_exec(
            self.command,
            *self.args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def send_message(self, message):
        data = json.dumps(message) + "\n"
        self.process.stdin.write(data.encode())
        await self.process.stdin.drain()

    async def receive_message(self):
        line = await self.process.stdout.readline()
        return json.loads(line.decode())
```

#### SSE Transport

```python
import aiohttp

class SSETransport:
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}
        self.session = None

    async def connect(self):
        self.session = aiohttp.ClientSession()

    async def send_message(self, message):
        async with self.session.post(
            f"{self.url}/messages",
            json=message,
            headers=self.headers
        ) as response:
            return await response.json()
```

### Error Handling

```python
from mcp.exceptions import MCPError

async def safe_tool_call(client, tool_name, arguments):
    try:
        result = await client.call_tool(tool_name, arguments)
        return result
    except MCPError as e:
        print(f"MCP Error: {e.message}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## For Server Developers

### Getting Started

MCP servers provide tools, resources, and prompts to client applications. They act as bridges between the MCP protocol and external systems, APIs, or data sources.

### Key Responsibilities

1. **Capability Exposure**: Define and expose tools, resources, and prompts
2. **Request Handling**: Process client requests and return appropriate responses
3. **Data Management**: Interface with external systems and data sources
4. **Error Handling**: Provide meaningful error messages and handle edge cases

### Basic Server Implementation

```python
from mcp import Server
import asyncio

# Create server instance
server = Server("example-server")

@server.tool("read_file")
async def read_file(path: str) -> str:
    """Read the contents of a file."""
    try:
        with open(path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise MCPError(f"File not found: {path}")
    except PermissionError:
        raise MCPError(f"Permission denied: {path}")

@server.resource("file://{path}")
async def get_file_resource(path: str):
    """Provide file contents as a resource."""
    try:
        with open(path, 'r') as f:
            content = f.read()
        return {
            "uri": f"file://{path}",
            "mimeType": "text/plain",
            "text": content
        }
    except Exception as e:
        raise MCPError(f"Could not read file: {e}")

@server.prompt("summarize")
async def summarize_prompt(topic: str = ""):
    """Generate a prompt for summarizing content."""
    return {
        "messages": [
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": f"Please summarize the following content about {topic}:"
                }
            }
        ]
    }

async def main():
    # Run the server
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### Tool Development

#### Input Validation

```python
from pydantic import BaseModel, validator

class FileReadInput(BaseModel):
    path: str
    encoding: str = "utf-8"

    @validator('path')
    def validate_path(cls, v):
        if not v or '..' in v:
            raise ValueError("Invalid path")
        return v

@server.tool("read_file")
async def read_file(input: FileReadInput) -> str:
    """Read file with proper validation."""
    # Implementation here
    pass
```

#### Error Handling

```python
@server.tool("risky_operation")
async def risky_operation(data: str):
    """Example of proper error handling."""
    try:
        # Perform operation
        result = process_data(data)
        return {"success": True, "result": result}
    except ValueError as e:
        raise MCPError(f"Invalid input: {e}")
    except Exception as e:
        # Log the actual error but don't expose internal details
        logger.error(f"Unexpected error in risky_operation: {e}")
        raise MCPError("An unexpected error occurred")
```

### Resource Development

#### Dynamic Resources

```python
@server.resource("database://tables/{table_name}")
async def get_table_schema(table_name: str):
    """Provide database table schema as a resource."""
    try:
        schema = await get_table_schema_from_db(table_name)
        return {
            "uri": f"database://tables/{table_name}",
            "mimeType": "application/json",
            "text": json.dumps(schema, indent=2)
        }
    except TableNotFoundError:
        raise MCPError(f"Table '{table_name}' not found")
```

#### Resource Subscriptions

```python
@server.resource("live://metrics")
async def live_metrics():
    """Provide live metrics that update over time."""
    def on_metrics_update(new_metrics):
        # Notify clients of resource update
        server.notify_resource_updated("live://metrics")

    # Set up metrics monitoring
    setup_metrics_monitoring(on_metrics_update)

    # Return current metrics
    return get_current_metrics()
```

### Prompt Development

```python
@server.prompt("code_review")
async def code_review_prompt(
    language: str = "python",
    focus: str = "general"
):
    """Generate a code review prompt."""
    focus_instructions = {
        "security": "Focus on security vulnerabilities and best practices.",
        "performance": "Focus on performance optimizations and efficiency.",
        "style": "Focus on code style and readability.",
        "general": "Provide a comprehensive code review."
    }

    instruction = focus_instructions.get(focus, focus_instructions["general"])

    return {
        "description": f"Code review prompt for {language} code",
        "messages": [
            {
                "role": "system",
                "content": {
                    "type": "text",
                    "text": f"You are an expert {language} developer. {instruction}"
                }
            },
            {
                "role": "user",
                "content": {
                    "type": "text",
                    "text": "Please review the following code:"
                }
            }
        ]
    }
```

## Debugging

### Inspector

The MCP Inspector is a powerful debugging tool that allows you to test and debug MCP servers interactively.

#### Installation

```bash
npm install -g @modelcontextprotocol/inspector
```

#### Usage

```bash
# Test a local server
mcp-inspector path/to/your/server.py

# Test with custom arguments
mcp-inspector python my_server.py --arg1 value1

# Test SSE server
mcp-inspector --transport sse http://localhost:8000/sse
```

#### Features

* **Interactive Testing**: Test tools, resources, and prompts
* **Real-time Validation**: Check protocol compliance
* **Error Debugging**: See detailed error messages
* **Performance Monitoring**: Track request/response times

### Logging

#### Server-side Logging

```python
import logging
from mcp import Server

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

server = Server("my-server")

@server.tool("debug_tool")
async def debug_tool(data: str):
    logger.info(f"debug_tool called with data: {data}")

    try:
        result = process_data(data)
        logger.debug(f"Processing successful: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in debug_tool: {e}", exc_info=True)
        raise
```

#### Client-side Logging

```python
import logging
from mcp import Client

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def debug_client():
    client = Client()

    # Enable request/response logging
    client.enable_debug_logging()

    await client.connect("stdio", {"command": "python", "args": ["server.py"]})

    # This will log the full request/response
    tools = await client.list_tools()
    logger.info(f"Retrieved {len(tools)} tools")
```

### Common Issues and Solutions

#### Connection Issues

```python
async def robust_connect(client, transport_config, max_retries=3):
    """Connect with retry logic."""
    for attempt in range(max_retries):
        try:
            await client.connect(transport_config)
            return True
        except ConnectionError as e:
            logger.warning(f"Connection attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
    return False
```

#### Tool Call Failures

```python
async def debug_tool_call(client, tool_name, arguments):
    """Debug a tool call with detailed error information."""
    try:
        # Validate tool exists
        tools = await client.list_tools()
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            print(f"Tool '{tool_name}' not found. Available tools: {[t.name for t in tools]}")
            return

        # Validate arguments against schema
        # ... validation logic ...

        # Make the call
        result = await client.call_tool(tool_name, arguments)
        return result

    except Exception as e:
        print(f"Tool call failed: {e}")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {arguments}")
        raise
```

## Testing

### Unit Testing Servers

```python
import pytest
from mcp import Server

@pytest.fixture
async def server():
    server = Server("test-server")

    @server.tool("add")
    async def add(a: int, b: int) -> int:
        return a + b

    return server

@pytest.mark.asyncio
async def test_add_tool(server):
    # Test the tool directly
    result = await server.call_tool("add", {"a": 2, "b": 3})
    assert result == 5

@pytest.mark.asyncio
async def test_tool_validation(server):
    # Test invalid input
    with pytest.raises(MCPError):
        await server.call_tool("add", {"a": "invalid", "b": 3})
```

### Integration Testing

```python
import pytest
from mcp import Client, Server

@pytest.mark.asyncio
async def test_client_server_integration():
    # Start server in background
    server = create_test_server()
    server_task = asyncio.create_task(server.run())

    try:
        # Wait for server to start
        await asyncio.sleep(0.1)

        # Connect client
        client = Client()
        await client.connect("stdio", {
            "command": "python",
            "args": ["test_server.py"]
        })

        # Test functionality
        tools = await client.list_tools()
        assert len(tools) > 0

        result = await client.call_tool("test_tool", {"param": "value"})
        assert result is not None

    finally:
        server_task.cancel()
```

## Best Practices

### Security

1. **Input Validation**: Always validate inputs
2. **Principle of Least Privilege**: Grant minimal necessary permissions
3. **Sandboxing**: Isolate dangerous operations
4. **Audit Logging**: Log security-relevant events
5. **Rate Limiting**: Prevent abuse

### Performance

1. **Async Operations**: Use async/await for I/O operations
2. **Connection Pooling**: Reuse connections when possible
3. **Caching**: Cache expensive operations
4. **Streaming**: Use streaming for large data transfers
5. **Pagination**: Implement pagination for large result sets

### Error Handling

1. **Graceful Degradation**: Handle errors gracefully
2. **Clear Messages**: Provide helpful error messages
3. **Logging**: Log errors for debugging
4. **Recovery**: Implement retry logic where appropriate
5. **User Feedback**: Give users actionable feedback

### Documentation

1. **Clear Descriptions**: Document all tools, resources, and prompts
2. **Examples**: Provide usage examples
3. **Schema Documentation**: Document input/output schemas
4. **Error Codes**: Document possible error conditions
5. **Changelog**: Maintain version history

## Architecture Patterns

### Microservices Architecture

```python
# Database service
@server.tool("query_database")
async def query_database(query: str) -> dict:
    return await db_service.execute_query(query)

# File service
@server.tool("read_file")
async def read_file(path: str) -> str:
    return await file_service.read_file(path)

# Authentication service
@server.tool("authenticate")
async def authenticate(token: str) -> dict:
    return await auth_service.validate_token(token)
```

### Plugin Architecture

```python
class PluginManager:
    def __init__(self, server):
        self.server = server
        self.plugins = {}

    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin
        plugin.register_with_server(self.server)

    def unregister_plugin(self, name):
        if name in self.plugins:
            self.plugins[name].unregister_from_server(self.server)
            del self.plugins[name]

class DatabasePlugin:
    def register_with_server(self, server):
        @server.tool("db_query")
        async def db_query(query: str):
            return await self.execute_query(query)

    async def execute_query(self, query: str):
        # Implementation
        pass
```

This comprehensive development guide should help both client and server developers understand how to work with MCP effectively. The examples provide practical starting points while the best practices ensure robust, secure implementations.