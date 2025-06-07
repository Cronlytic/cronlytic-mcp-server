# Core MCP Concepts

This document covers the core concepts of the Model Context Protocol (MCP) including prompts, resources, tools, sampling, transports, and roots.

## Prompts

Prompts in MCP are interactive templates that help users gather context before sending requests to language models. They provide a structured way to collect inputs and assemble complete prompts with context.

### User Interaction Model

Prompts in MCP are designed to be **user-centric and transparent**, with the human ultimately in control of what gets sent to the language model.

Implementations typically expose prompts through:

* Searchable lists in user interfaces
* Quick access mechanisms (shortcuts, commands)
* Integration with existing prompt/command systems

![Example prompt workflow](https://mintlify.s3.us-west-1.amazonaws.com/mcp/specification/draft/server/prompt-flow.png)

Applications might implement prompts through various interface patterns including lists, search, command palettes, or direct invocation - the protocol itself does not mandate any specific user interaction model.

### Protocol Messages

#### Listing Prompts

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "prompts/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "prompts": [
      {
        "name": "git-commit",
        "description": "Generate a commit message from staged changes",
        "arguments": [
          {
            "name": "type",
            "description": "Type of commit (feat, fix, docs, etc.)",
            "required": true
          }
        ]
      }
    ]
  }
}
```

#### Getting Prompts

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "prompts/get",
  "params": {
    "name": "git-commit",
    "arguments": {
      "type": "feat"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "description": "Generate a commit message",
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "Generate a commit message for these changes:\n\n[staged changes content]"
        }
      }
    ]
  }
}
```

---

## Resources

Resources provide contextual data that language models can use to enhance their responses. They represent files, database schemas, API documentation, or any other information that provides relevant context.

### User Interaction Model

Resources in MCP are designed to be **application-driven**, with host applications determining how to incorporate context based on their needs.

Applications could:

* Expose resources through UI elements for explicit selection
* Allow searching through and filtering available resources
* Implement automatic context inclusion based on heuristics

### Protocol Messages

#### Listing Resources

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "resources/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "resources": [
      {
        "uri": "file:///project/src/main.rs",
        "name": "main.rs",
        "description": "Primary application entry point",
        "mimeType": "text/x-rust"
      }
    ]
  }
}
```

#### Reading Resources

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "resources/read",
  "params": {
    "uri": "file:///project/src/main.rs"
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "contents": [
      {
        "uri": "file:///project/src/main.rs",
        "mimeType": "text/x-rust",
        "text": "fn main() {\n    println!(\"Hello world!\");\n}"
      }
    ]
  }
}
```

---

## Tools

Tools enable language models to interact with external systems and perform actions beyond generating text. They allow models to fetch data, execute commands, modify files, and more.

### User Interaction Model

Tools in MCP can be invoked through various patterns:

* Direct user approval for each tool call
* Automatic execution for trusted tools
* Sandboxed execution environments
* Human-in-the-loop workflows

<Warning>
  Applications **SHOULD** implement appropriate safeguards around tool execution, including:

  * User confirmation for potentially dangerous operations
  * Sandboxing or containerization for tool execution
  * Rate limiting and access controls
  * Audit logging for tool invocations
</Warning>

### Protocol Messages

#### Listing Tools

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "read_file",
        "description": "Read the contents of a file",
        "inputSchema": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "Path to the file to read"
            }
          },
          "required": ["path"]
        }
      }
    ]
  }
}
```

#### Calling Tools

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "read_file",
    "arguments": {
      "path": "/home/user/document.txt"
    }
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "Contents of the file..."
      }
    ]
  }
}
```

---

## Sampling

Sampling enables MCP servers to request language model generations from clients. This powerful feature allows servers to implement agentic behaviors while keeping the client in control of model access and selection.

### User Interaction Model

<Warning>
  For trust & safety and security, there **SHOULD** always be a human in the loop with the ability to deny sampling requests.

  Applications **SHOULD**:

  * Provide UI that makes it easy and intuitive to review sampling requests
  * Allow users to view and edit prompts before sending
  * Present generated responses for review before delivery
</Warning>

### Protocol Messages

#### Creating Messages

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "sampling/createMessage",
  "params": {
    "messages": [
      {
        "role": "user",
        "content": {
          "type": "text",
          "text": "What is the capital of France?"
        }
      }
    ],
    "modelPreferences": {
      "hints": [
        {
          "name": "claude-3-sonnet"
        }
      ],
      "intelligencePriority": 0.8,
      "speedPriority": 0.5
    },
    "maxTokens": 100
  }
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "role": "assistant",
    "content": {
      "type": "text",
      "text": "The capital of France is Paris."
    },
    "model": "claude-3-sonnet-20240307",
    "stopReason": "endTurn"
  }
}
```

---

## Transports

MCP supports multiple transport mechanisms to establish communication between clients and servers:

### Standard Input/Output (stdio)

The simplest transport where the server process uses standard input/output for communication.

**Characteristics:**
* Local execution only
* Process-based communication
* Automatic lifecycle management
* No network configuration required

### Server-Sent Events (SSE)

HTTP-based transport using Server-Sent Events for bidirectional communication.

**Characteristics:**
* Network-based communication
* Web-compatible transport
* Firewall-friendly (HTTP-based)
* Supports authentication headers

### WebSocket Transport

Real-time bidirectional communication over WebSockets.

**Characteristics:**
* Low-latency communication
* Full duplex communication
* Connection-based protocol
* Suitable for real-time applications

---

## Roots

Roots provide a mechanism for servers to request access to specific directories or file system locations. This enables secure, controlled access to local resources.

### User Interaction Model

Roots work on an **approval-based model**:

1. Server requests access to specific directories
2. Client prompts user for approval
3. User grants or denies access
4. Server operates within approved boundaries

### Protocol Messages

#### Listing Roots

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "roots/list"
}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "roots": [
      {
        "uri": "file:///approved/directory",
        "name": "Project Directory"
      }
    ]
  }
}
```

---

## Best Practices

### Security Considerations

1. **Always validate inputs** - Check all parameters and arguments
2. **Implement user approval** - For sensitive operations
3. **Use least privilege** - Grant minimal necessary permissions
4. **Audit operations** - Log important actions
5. **Handle errors gracefully** - Provide clear error messages

### Performance Guidelines

1. **Implement pagination** - For large result sets
2. **Cache when appropriate** - Reduce redundant operations
3. **Use efficient serialization** - Minimize data transfer
4. **Handle timeouts** - Set reasonable operation limits
5. **Monitor resource usage** - Track memory and CPU consumption

### User Experience

1. **Provide clear descriptions** - Help users understand capabilities
2. **Use intuitive naming** - Make functions discoverable
3. **Handle edge cases** - Graceful degradation
4. **Responsive design** - Work across different interfaces
5. **Accessibility** - Support assistive technologies