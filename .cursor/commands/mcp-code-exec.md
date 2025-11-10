# MCP Code Execution Pattern - Implementation Guide

Your task is to convert an MCP server into the **Code Execution Pattern** described in [Anthropic's blog post](https://www.anthropic.com/engineering/code-execution-with-mcp). This pattern enables **progressive disclosure** of tools, reducing token usage by up to 98% compared to loading all tools upfront.

---

## Why This Pattern?

**Problem with Traditional MCP:**

- Loading all tools upfront consumes 150,000+ tokens
- Intermediate tool results flow through model context repeatedly
- Agents slow down with many connected tools

**Solution - Code Execution Pattern:**

- Tools organized as importable Python modules (filesystem-based)
- Agents load only what they need (progressive disclosure)
- Data processing happens in code before returning to model
- **Result**: 98.7% token reduction (150K → 2K tokens)

---

## Step-by-Step Implementation

### Step 1: Create Folder Structure

Create a dedicated folder for the MCP server in `./servers/` directory:

```
./servers/[server_name]/
├── server.py           # Server singleton & connection management (with discovery in __main__)
├── [tool_1].py         # Individual tool file (with test in __main__)
├── [tool_2].py         # Individual tool file (with test in __main__)
├── [tool_3].py         # Individual tool file (with test in __main__)
└── __init__.py         # Package exports
```

**Example:**

```
./servers/notion/
├── server.py
├── search.py
├── fetch.py
├── create_pages.py
└── __init__.py
```

**Create the folder:**

```bash
mkdir -p ./servers/[server_name]
```

---

### Step 2: Create the Server Module

The `server.py` module manages the MCP server connection as a singleton. Include tool discovery in the `__main__` block to list available tools.

**Note:** This pattern works with **any MCP server type**. The template below shows `MCPServerStdio` (most common), but you can use:

- `MCPServerStdio` - Local scripts, npm packages, or OAuth servers with `mcp-remote`
- `MCPServerSse` - Server-Sent Events servers
- `MCPServerStreamableHttp` - HTTP streaming servers
- `HostedMCPTool` - Publicly accessible servers (no need for singleton pattern)

See `.cursor/commands/add-mcp.md` for detailed configuration of each server type.

**Template (`./servers/[server_name]/server.py`):**

```python
"""[Server Name] MCP Server Configuration"""
# Choose the appropriate import based on your server type:
from agents.mcp import MCPServerStdio  # For local scripts, npm packages, or mcp-remote
# from agents.mcp import MCPServerSse  # For Server-Sent Events servers
# from agents.mcp import MCPServerStreamableHttp  # For HTTP streaming servers
# from agency_swarm import HostedMCPTool  # For publicly accessible servers (different pattern)

from typing import Optional

# Singleton server instance
_server: Optional[MCPServerStdio] = None  # Adjust type if using different server
_connected: bool = False

def get_server() -> MCPServerStdio:  # Adjust return type if using different server
    """Get the [Server Name] MCP server instance (singleton)"""
    global _server
    if _server is None:
        # Example: Stdio server with mcp-remote (OAuth)
        _server = MCPServerStdio(
            name="[Server_Name]",
            params={
                "command": "npx",  # or "python", "node", etc.
                "args": ["-y", "mcp-remote", "https://your-server.com/mcp"],
                # Add env vars if needed:
                # "env": {
                #     "API_KEY": os.getenv("API_KEY_NAME")
                # }
            },
            cache_tools_list=True,
            client_session_timeout_seconds=30  # Increase for OAuth
        )

        # Example: SSE server
        # _server = MCPServerSse(
        #     name="[Server_Name]",
        #     params={
        #         "url": "http://localhost:8000/sse",
        #         "headers": {"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
        #     },
        #     cache_tools_list=True
        # )

        # Example: Remote HTTP server
        # _server = HostedMCPTool(
        #     name="[Server_Name]",
        #     tool_config={
        #         "type": "mcp",
        #         "server_label": "[Server_Name]",
        #         "server_url": "https://your-server.com/mcp",
        #         "require_approval": "never",
        #         "headers": {
        #             "Authorization": f"Bearer {os.getenv('API_TOKEN')}"
        #         }
        #     }
        # )

        # Example: Remote OAuth server
        # _server = MCPServerStdio(
        #     name="[Server_Name]",
        #     params={
        #         "command": "npx",
        #         "args": ["-y", "mcp-remote", "https://your-server.com/mcp"],
        #         "env": {
        #             "MCP_REMOTE_CONFIG_DIR": os.path.join(folder_path, "mnt", "mcp_credentials") # persistent storage for OAuth credentials, don't add to .gitignore
        #         }
        #     },
        #     cache_tools_list=True,
        #     client_session_timeout_seconds=30
        # )
    return _server

async def ensure_connected() -> MCPServerStdio:  # Adjust return type if using different server
    """Ensure the server is connected, connect if not"""
    global _connected
    server = get_server()

    if not _connected:
        await server.connect()
        _connected = True

    return server

async def call_tool(tool_name: str, arguments: dict):
    """Call a tool on the MCP server with the given arguments"""
    server = await ensure_connected()

    # Get the session
    session = getattr(server, 'session', None) or getattr(server, '_client_session', None)
    if not session:
        raise RuntimeError("Could not access MCP session")

    # Call the tool
    result = await session.call_tool(name=tool_name, arguments=arguments)

    # Extract content from result
    if hasattr(result, 'content'):
        content = result.content
        if isinstance(content, list) and len(content) > 0:
            return content[0].text if hasattr(content[0], 'text') else str(content[0])
        return str(content)

    return result

# Tool discovery - run with: python ./servers/[server_name]/server.py
if __name__ == "__main__":
    import asyncio

    async def discover_tools():
        print("Discovering tools from MCP server...")
        server = await ensure_connected()

        session = getattr(server, 'session', None) or getattr(server, '_client_session', None)
        if session:
            tools_result = await session.list_tools()
            tools = tools_result.tools if hasattr(tools_result, 'tools') else []

            print(f"\nFound {len(tools)} tools:\n")
            for tool in tools:
                print(f"Tool: {tool.name}")
                print(f"  Description: {tool.description}")
                if hasattr(tool, 'inputSchema') and 'properties' in tool.inputSchema:
                    print(f"  Parameters:")
                    schema = tool.inputSchema
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'any')
                        param_desc = param_info.get('description', '')
                        required = param_name in schema.get('required', [])
                        print(f"    - {param_name}: {param_type} {'(required)' if required else '(optional)'}")
                        if param_desc:
                            print(f"      {param_desc}")
                print()

    asyncio.run(discover_tools())
```

**Run discovery:**

```bash
python ./servers/[server_name]/server.py
```

This will list all available tools with their descriptions and parameters. Use this output to create individual tool files.

---

### Step 3: Create Individual Tool Files

For each tool discovered by running `server.py`, create a dedicated Python file. **Use the exact descriptions and parameters from the MCP server output** - don't add examples or extra documentation unless provided by the MCP server.

**Template (`./servers/[server_name]/[tool_name].py`):**

```python
"""
[Tool description from MCP server]
"""
from typing import Optional, Dict, List, Any
from .server import call_tool


async def [tool_name](
    required_param: str,
    optional_param: Optional[str] = None,
    another_param: Optional[Dict[str, Any]] = None
) -> str:
    """
    [Tool description from MCP server]

    Args:
        required_param: [Parameter description from MCP]
        optional_param: [Parameter description from MCP]
        another_param: [Parameter description from MCP]

    Returns:
        Tool result as string
    """
    # Build arguments dict with required params
    arguments = {"required_param": required_param}

    # Add optional params only if provided
    if optional_param:
        arguments["optional_param"] = optional_param
    if another_param:
        arguments["another_param"] = another_param

    # Call the MCP tool
    return await call_tool("[mcp-tool-name]", arguments)


# Test - run with: python ./servers/[server_name]/[tool_name].py
if __name__ == "__main__":
    import asyncio

    async def test():
        print("Testing [tool_name]...")
        try:
            result = await [tool_name]("test_value")
            print(f"✓ Success: {str(result)[:200]}...")
        except Exception as e:
            print(f"✗ Error: {e}")

    asyncio.run(test())
```

---

### Step 4: Create Package Exports

The `__init__.py` file makes tools easily importable.

**Template (`./servers/[server_name]/__init__.py`):**

```python
"""
[Server Name] MCP Tools

Progressive disclosure pattern - import only what you need.
See: https://www.anthropic.com/engineering/code-execution-with-mcp
"""

# Server management
from .server import get_server, ensure_connected, call_tool

# Individual tools
from .[tool_1] import [tool_1]
from .[tool_2] import [tool_2]
from .[tool_3] import [tool_3]
# ... more imports

__all__ = [
    # Server
    "get_server",
    "ensure_connected",
    "call_tool",
    # Tools
    "[tool_1]",
    "[tool_2]",
    "[tool_3]",
    # ... more exports
]
```

---

### Step 5: Test the Implementation

Test the implementation by specific tools using the following command:

```bash
python ./servers/[server_name]/[tool_name].py
```

Only run fetch tools, do not update, create any data.

## Troubleshooting

### Tools not connecting

**Symptom**: `RuntimeError: Could not access MCP session`

**Fix**:

1. Check server.py is correctly implemented
2. Verify session access: try both `server.session` and `server._client_session`
3. Ensure `await ensure_connected()` is called before tool use

### OAuth timeout (Important!)

**Symptom**: `McpError: Timed out while waiting for response`

**Fix**: Increase `client_session_timeout_seconds` to 30 or higher in server.py

---

## Quick Checklist

- [ ] Create `./servers/[server_name]/` folder
- [ ] Implement `server.py` with singleton pattern and discovery in `__main__`
- [ ] Run `python ./servers/[server_name]/server.py` to discover tools
- [ ] Create individual tool files using descriptions from MCP server output
- [ ] Add `if __name__ == "__main__"` test blocks to each tool file
- [ ] Create `__init__.py` with exports
- [ ] Test individual tools: `python ./servers/[server_name]/[tool].py`

---

## References

- [Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Agency Swarm MCP Integration](https://agency-swarm.ai/core-framework/tools/mcp-integration)
- [Adding MCP Servers to Agents](.cursor/commands/add-mcp.md)
