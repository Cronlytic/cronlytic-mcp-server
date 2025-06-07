# Example Servers and FAQs

This document provides examples of MCP servers and answers to frequently asked questions about implementing and using the Model Context Protocol.

## Example Servers

MCP servers are available to provide tools, resources, and prompts to client applications. The community has created many servers for various use cases.

### Installation Methods

#### Using uvx (Recommended)
```bash
# Install a server using uvx
uvx mcp-server-git

# Install with specific arguments
uvx --from mcp-server-sqlite mcp-server-sqlite --db-path ./test.db
```

#### Using pip
```bash
# Install directly with pip
pip install mcp-server-git

# Run the server
python -m mcp_server_git --repository /path/to/repo
```

### Popular Example Servers

#### File System Server
```python
#!/usr/bin/env python3
"""
Example MCP server for file system operations.
"""

import asyncio
import json
import os
from pathlib import Path
from mcp.server import Server
from mcp.types import Tool, Resource

# Create server instance
server = Server("filesystem")

@server.list_tools()
async def list_tools():
    """List available file system tools."""
    return [
        Tool(
            name="read_file",
            description="Read the contents of a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="write_file",
            description="Write content to a file",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to write"
                    },
                    "content": {
                        "type": "string",
                        "description": "Content to write to the file"
                    }
                },
                "required": ["path", "content"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "read_file":
        path = arguments["path"]
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [{"type": "text", "text": content}]
        except FileNotFoundError:
            return [{"type": "text", "text": f"Error: File '{path}' not found"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error reading file: {str(e)}"}]

    elif name == "write_file":
        path = arguments["path"]
        content = arguments["content"]
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return [{"type": "text", "text": f"Successfully wrote to '{path}'"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error writing file: {str(e)}"}]

    else:
        return [{"type": "text", "text": f"Unknown tool: {name}"}]

@server.list_resources()
async def list_resources():
    """List available file resources."""
    resources = []
    # Add some example file resources
    for ext in ['.py', '.js', '.md', '.txt']:
        for root, dirs, files in os.walk('.'):
            for file in files:
                if file.endswith(ext):
                    file_path = os.path.join(root, file)
                    resources.append(Resource(
                        uri=f"file://{os.path.abspath(file_path)}",
                        name=file,
                        description=f"{ext.upper()} file",
                        mimeType="text/plain"
                    ))
    return resources

@server.read_resource()
async def read_resource(uri: str):
    """Read a file resource."""
    if uri.startswith("file://"):
        file_path = uri[7:]  # Remove "file://" prefix
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return [{"uri": uri, "mimeType": "text/plain", "text": content}]
        except Exception as e:
            raise ValueError(f"Could not read file: {str(e)}")
    else:
        raise ValueError(f"Unsupported URI scheme: {uri}")

if __name__ == "__main__":
    asyncio.run(server.run())
```

#### Web Search Server
```python
#!/usr/bin/env python3
"""
Example MCP server for web search functionality.
"""

import asyncio
import aiohttp
import json
from mcp.server import Server
from mcp.types import Tool

server = Server("web-search")

@server.list_tools()
async def list_tools():
    """List available web search tools."""
    return [
        Tool(
            name="web_search",
            description="Search the web for information",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "num_results": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_page_content",
            description="Get the text content of a web page",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "URL of the page to fetch"
                    }
                },
                "required": ["url"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if name == "web_search":
        query = arguments["query"]
        num_results = arguments.get("num_results", 5)

        # This is a mock implementation - in a real server you'd use
        # a search API like Google Custom Search, Bing, etc.
        results = [
            {
                "title": f"Search result {i+1} for '{query}'",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a mock search result snippet for query '{query}'"
            }
            for i in range(num_results)
        ]

        formatted_results = "\n\n".join([
            f"**{result['title']}**\n{result['url']}\n{result['snippet']}"
            for result in results
        ])

        return [{"type": "text", "text": formatted_results}]

    elif name == "get_page_content":
        url = arguments["url"]

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.content_type.startswith('text/'):
                        content = await response.text()
                        # In a real implementation, you'd want to extract
                        # just the main text content, not the full HTML
                        return [{"type": "text", "text": content[:2000] + "..."}]
                    else:
                        return [{"type": "text", "text": f"Cannot read non-text content from {url}"}]
        except Exception as e:
            return [{"type": "text", "text": f"Error fetching page: {str(e)}"}]

    else:
        return [{"type": "text", "text": f"Unknown tool: {name}"}]

if __name__ == "__main__":
    asyncio.run(server.run())
```

#### Database Server
```python
#!/usr/bin/env python3
"""
Example MCP server for database operations.
"""

import asyncio
import sqlite3
import json
from mcp.server import Server
from mcp.types import Tool, Resource

server = Server("database")

# Global database connection
db_connection = None

async def init_database():
    """Initialize database connection."""
    global db_connection
    db_connection = sqlite3.connect("example.db")
    db_connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE
        )
    """)
    db_connection.commit()

@server.list_tools()
async def list_tools():
    """List available database tools."""
    return [
        Tool(
            name="execute_query",
            description="Execute a SQL query (SELECT only for safety)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (SELECT statements only)"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="describe_table",
            description="Get the schema of a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls."""
    if not db_connection:
        await init_database()

    if name == "execute_query":
        query = arguments["query"].strip()

        # For safety, only allow SELECT queries
        if not query.upper().startswith("SELECT"):
            return [{"type": "text", "text": "Error: Only SELECT queries are allowed for safety"}]

        try:
            cursor = db_connection.execute(query)
            rows = cursor.fetchall()
            column_names = [description[0] for description in cursor.description]

            if not rows:
                return [{"type": "text", "text": "Query executed successfully, but no rows returned"}]

            # Format results as a table
            result = f"Columns: {', '.join(column_names)}\n\n"
            for row in rows:
                result += " | ".join(str(cell) for cell in row) + "\n"

            return [{"type": "text", "text": result}]

        except Exception as e:
            return [{"type": "text", "text": f"Error executing query: {str(e)}"}]

    elif name == "describe_table":
        table_name = arguments["table_name"]

        try:
            cursor = db_connection.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            if not columns:
                return [{"type": "text", "text": f"Table '{table_name}' not found"}]

            result = f"Schema for table '{table_name}':\n\n"
            for col in columns:
                result += f"- {col[1]} ({col[2]}) {'NOT NULL' if col[3] else 'NULL'}\n"

            return [{"type": "text", "text": result}]

        except Exception as e:
            return [{"type": "text", "text": f"Error describing table: {str(e)}"}]

    elif name == "list_tables":
        try:
            cursor = db_connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            tables = cursor.fetchall()

            if not tables:
                return [{"type": "text", "text": "No tables found in the database"}]

            table_list = "\n".join([f"- {table[0]}" for table in tables])
            return [{"type": "text", "text": f"Tables in database:\n\n{table_list}"}]

        except Exception as e:
            return [{"type": "text", "text": f"Error listing tables: {str(e)}"}]

    else:
        return [{"type": "text", "text": f"Unknown tool: {name}"}]

@server.list_resources()
async def list_resources():
    """List available database resources."""
    if not db_connection:
        await init_database()

    try:
        cursor = db_connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = cursor.fetchall()

        resources = []
        for table in tables:
            table_name = table[0]
            resources.append(Resource(
                uri=f"db://table/{table_name}",
                name=f"Table: {table_name}",
                description=f"Database table '{table_name}'",
                mimeType="application/json"
            ))

        return resources

    except Exception:
        return []

@server.read_resource()
async def read_resource(uri: str):
    """Read a database resource."""
    if not uri.startswith("db://table/"):
        raise ValueError(f"Unsupported URI: {uri}")

    table_name = uri.split("/")[-1]

    try:
        # Get table schema
        cursor = db_connection.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        # Get sample data (first 10 rows)
        cursor = db_connection.execute(f"SELECT * FROM {table_name} LIMIT 10")
        rows = cursor.fetchall()
        column_names = [description[0] for description in cursor.description]

        schema_info = {
            "table": table_name,
            "columns": [
                {
                    "name": col[1],
                    "type": col[2],
                    "nullable": not col[3],
                    "primary_key": bool(col[5])
                }
                for col in columns
            ],
            "sample_data": [
                dict(zip(column_names, row)) for row in rows
            ]
        }

        return [{
            "uri": uri,
            "mimeType": "application/json",
            "text": json.dumps(schema_info, indent=2)
        }]

    except Exception as e:
        raise ValueError(f"Could not read table: {str(e)}")

if __name__ == "__main__":
    asyncio.run(server.run())
```

## FAQs

### General Questions

#### What is MCP?

The Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. It provides a standardized way to connect language models with the context they need.

#### How does MCP differ from other integration methods?

MCP provides:
- **Standardization**: A common protocol that works across different LLM applications
- **Security**: Built-in security features and user control
- **Flexibility**: Support for various transport methods and data types
- **Extensibility**: Easy to add new tools and resources

#### What are the main components of MCP?

MCP has three main components:
1. **Tools**: Functions that language models can call to perform actions
2. **Resources**: Contextual data that can be provided to language models
3. **Prompts**: Template systems for creating structured interactions

### Implementation Questions

#### How do I create my first MCP server?

1. Choose your programming language (Python or TypeScript are officially supported)
2. Install the MCP SDK
3. Define your tools, resources, or prompts
4. Run your server

Here's a minimal Python example:

```python
from mcp.server import Server

server = Server("my-first-server")

@server.list_tools()
async def list_tools():
    return [{"name": "hello", "description": "Say hello"}]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "hello":
        return [{"type": "text", "text": "Hello, World!"}]

if __name__ == "__main__":
    import asyncio
    asyncio.run(server.run())
```

#### What's the difference between tools and resources?

- **Tools**: Allow the LLM to perform actions (like reading files, making API calls, executing commands)
- **Resources**: Provide static or dynamic context to the LLM (like file contents, database schemas, documentation)

#### How do I handle authentication in my MCP server?

Authentication depends on your transport method:

For SSE transport:
```python
# Check headers for authentication
def authenticate_request(headers):
    token = headers.get('Authorization', '').replace('Bearer ', '')
    if not verify_token(token):
        raise ValueError("Invalid authentication")

@server.call_tool()
async def call_tool(name: str, arguments: dict, context: dict = None):
    # Access headers from context
    authenticate_request(context.get('headers', {}))
    # Tool implementation...
```

For stdio transport, authentication typically happens at the process level.

#### How do I test my MCP server?

Use the MCP Inspector:

```bash
# Install the inspector
npm install -g @modelcontextprotocol/inspector

# Test your server
mcp-inspector path/to/your/server.py

# Test with arguments
mcp-inspector python server.py --arg value
```

#### How do I configure my MCP server with Claude Desktop?

1. Open Claude Desktop configuration file:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. Add your server configuration:
```json
{
  "mcpServers": {
    "my-server": {
      "command": "python",
      "args": ["path/to/my/server.py"]
    }
  }
}
```

3. Restart Claude Desktop

#### Can I use multiple MCP servers simultaneously?

Yes! Most MCP clients support multiple servers. Each server can provide different sets of tools and resources.

#### How do I handle errors in my MCP server?

Use appropriate error handling and return meaningful error messages:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        # Tool implementation
        return [{"type": "text", "text": "Success!"}]
    except FileNotFoundError:
        return [{"type": "text", "text": "Error: File not found"}]
    except PermissionError:
        return [{"type": "text", "text": "Error: Permission denied"}]
    except Exception as e:
        return [{"type": "text", "text": f"Unexpected error: {str(e)}"}]
```

### Performance Questions

#### How do I optimize my MCP server for performance?

1. **Use async/await**: Make your server asynchronous for better concurrency
2. **Implement caching**: Cache expensive operations
3. **Limit resource usage**: Implement timeouts and resource limits
4. **Use pagination**: For large result sets

```python
import asyncio
from functools import lru_cache

@lru_cache(maxsize=100)
def expensive_operation(param):
    # Cached expensive operation
    pass

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Use asyncio for concurrent operations
    tasks = [async_operation(arg) for arg in arguments['items']]
    results = await asyncio.gather(*tasks)
    return results
```

#### How do I handle large files or datasets?

1. **Streaming**: Use streaming for large files
2. **Pagination**: Break large datasets into pages
3. **Lazy loading**: Load data only when needed

```python
@server.read_resource()
async def read_resource(uri: str):
    if uri.startswith("large-file://"):
        # Stream large files in chunks
        with open(file_path, 'r') as f:
            content = f.read(1024 * 1024)  # Read 1MB at a time
            return [{"uri": uri, "text": content, "partial": True}]
```

### Security Questions

#### How do I secure my MCP server?

1. **Validate all inputs**: Never trust client input
2. **Use allowlists**: Restrict access to specific files/directories
3. **Implement authentication**: Verify client identity
4. **Sandbox operations**: Limit what your server can do

```python
import os
from pathlib import Path

ALLOWED_DIRECTORIES = ["/safe/directory", "/another/safe/path"]

def validate_path(path):
    """Validate that path is within allowed directories."""
    abs_path = os.path.abspath(path)
    for allowed in ALLOWED_DIRECTORIES:
        if abs_path.startswith(os.path.abspath(allowed)):
            return True
    raise ValueError(f"Access denied: {path}")

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "read_file":
        path = arguments["path"]
        validate_path(path)  # Security check
        # Safe to proceed...
```

#### What should I avoid in my MCP server?

1. **Don't execute arbitrary code**: Never use `eval()` or `exec()` with user input
2. **Don't expose sensitive data**: Be careful with environment variables, credentials
3. **Don't trust user input**: Always validate and sanitize
4. **Don't ignore resource limits**: Implement timeouts and limits

### Troubleshooting

#### My MCP server isn't connecting

1. Check the command path and arguments
2. Verify the server starts correctly when run manually
3. Check for import errors or missing dependencies
4. Look at the client logs for error messages

#### Tools aren't appearing in my client

1. Verify your `list_tools()` function returns the correct format
2. Check that your server responds to the initialization handshake
3. Ensure your tool schemas are valid JSON Schema

#### Resources aren't loading

1. Check your `list_resources()` and `read_resource()` implementations
2. Verify URI formats are correct
3. Ensure the client supports the resource types you're providing

### Best Practices

#### What are the best practices for MCP server development?

1. **Clear documentation**: Document all tools, resources, and their parameters
2. **Error handling**: Provide helpful error messages
3. **Input validation**: Always validate user inputs
4. **Performance**: Implement timeouts and resource limits
5. **Security**: Follow security best practices
6. **Testing**: Use the MCP Inspector and write tests
7. **Logging**: Add appropriate logging for debugging

#### How should I structure my MCP server project?

```
my-mcp-server/
├── src/
│   ├── __init__.py
│   ├── server.py          # Main server implementation
│   ├── tools/             # Tool implementations
│   │   ├── __init__.py
│   │   ├── file_tools.py
│   │   └── api_tools.py
│   ├── resources/         # Resource implementations
│   │   ├── __init__.py
│   │   └── data_resources.py
│   └── utils/             # Utility functions
│       ├── __init__.py
│       ├── auth.py
│       └── validation.py
├── tests/                 # Test files
├── requirements.txt       # Dependencies
├── README.md             # Documentation
└── pyproject.toml        # Project configuration
```

This comprehensive guide should help you understand MCP better and implement your own servers effectively!