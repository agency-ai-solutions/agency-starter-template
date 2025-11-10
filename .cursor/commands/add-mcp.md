# MCP Server Creation Task

Your task is to add Model Context Protocol (MCP) server to an Agency Swarm agent. MCP servers expose external tools and data sources to agents through a standardized protocol.

---

## Quick Reference: MCP Server Types

| Server Type               | When to Use                                | URL Pattern              | Class to Use                    |
| ------------------------- | ------------------------------------------ | ------------------------ | ------------------------------- |
| **Hosted Remote**         | Publicly accessible web service            | Any public URL           | `HostedMCPTool`                 |
| **Hosted Remote (OAuth)** | Publicly accessible web service with OAuth | Any public URL           | `MCPServerStdio` + `mcp-remote` |
| **Streamable HTTP**       | HTTP streaming server                      | Ends in `/mcp`           | `MCPServerStreamableHttp`       |
| **SSE**                   | Server-Sent Events server                  | Ends in `/sse`           | `MCPServerSse`                  |
| **Local/Stdio**           | GitHub repo, local script, or CLI tool     | GitHub URL or local path | `MCPServerStdio`                |

---

## Step-by-Step Process

### Step 1: Determine Server Type

**If user provides a URL:**

- Check if it's a public/internet-accessible URL:
  - **Requires OAuth authentication?** → Use `mcp-remote` with `MCPServerStdio`
  - **No authentication or token-based auth?** → Use `HostedMCPTool`
- Check if URL ends with `/mcp` → Use `MCPServerStreamableHttp` (or `HostedMCPTool` if public)
- Check if URL ends with `/sse` → Use `MCPServerSse` (or `HostedMCPTool` if public)

**If user provides a GitHub URL or mentions "local":**

- Use `MCPServerStdio`

**If unclear, ask:**

1. Is this a publicly accessible URL? (HostedMCPTool or mcp-remote)
2. Does it require OAuth authentication? (Use mcp-remote)
3. Is this a local server you'll run? (MCPServerStdio, MCPServerSse, or MCPServerStreamableHttp)
4. What's the server endpoint URL? (check `/mcp` or `/sse` suffix)
5. Which agent do you want to add this MCP server to?

---

### Step 2: Install and Setup Server (for Local/Stdio only)

**For GitHub repositories:**

1. Clone the repository to a local directory within your project:

```bash
git clone <repository-url> ./mcp_servers/<server-name>
```

2. Install dependencies (check the repo's README):

```bash
cd ./mcp_servers/<server-name>
# Common patterns:
npm install  # for Node.js servers
pip install -r requirements.txt  # for Python servers
uv sync  # for uv-based Python projects
```

3. Note the command needed to run the server (from README):

   - Node.js: `npx`, `node`, or `npm run`
   - Python: `python`, `uv run`, or `poetry run`

4. Check if API keys are needed and add them to `.env` file

**For existing npm packages:**

```bash
# No installation needed, use npx with -y flag
# Example: npx -y @modelcontextprotocol/server-filesystem
```

---

### Step 3: Add Server Configuration to Agent

Based on server type, add the appropriate configuration:

#### Option A: Hosted Remote Server (HostedMCPTool)

**When to use:** Server is publicly accessible on the internet.

```python
import os
from agency_swarm import Agent, HostedMCPTool

# Define the hosted MCP tool
hosted_mcp = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "descriptive-server-name",  # Choose descriptive name
        "server_url": "https://your-server.com/mcp/",  # or /sse/
        "require_approval": "never",  # or "always" for sensitive operations
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN_NAME')}"  # if auth required
        }
    }
)

# Add to agent's tools parameter (NOT mcp_servers)
agent = Agent(
    name="AgentName",
    description="Agent description",
    instructions="./instructions.md",
    tools=[hosted_mcp],  # Add to tools list
    model="gpt-5"
)
```

**Important:** HostedMCPTool goes in the `tools` parameter, not `mcp_servers`!

#### Option B: Local SSE Server (MCPServerSse)

**When to use:** Server runs locally or on private network with SSE transport.

```python
import os
from agency_swarm import Agent
from agents.mcp import MCPServerSse

# Define the SSE server
sse_server = MCPServerSse(
    name="Descriptive Server Name",
    params={
        "url": "http://localhost:8000/sse",  # Local or internal URL
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN_NAME')}",  # if needed
            "X-Custom-Header": "value"  # any custom headers
        }
    },
    cache_tools_list=True  # REQUIRED: Enable caching
)

# Add to agent's mcp_servers parameter
agent = Agent(
    name="AgentName",
    description="Agent description",
    instructions="./instructions.md",
    mcp_servers=[sse_server],  # Add to mcp_servers list
    model="gpt-5"
)
```

#### Option C: Local Streamable HTTP Server (MCPServerStreamableHttp)

**When to use:** Server uses HTTP POST with streaming responses.

```python
import os
from agency_swarm import Agent
from agents.mcp import MCPServerStreamableHttp

# Define the streamable HTTP server
http_server = MCPServerStreamableHttp(
    name="Descriptive Server Name",
    params={
        "url": "http://localhost:8000/mcp/",  # Usually ends in /mcp
        "headers": {
            "Authorization": f"Bearer {os.getenv('API_TOKEN_NAME')}"  # if needed
        }
    },
    cache_tools_list=True  # REQUIRED: Enable caching
)

# Add to agent's mcp_servers parameter
agent = Agent(
    name="AgentName",
    description="Agent description",
    instructions="./instructions.md",
    mcp_servers=[http_server],  # Add to mcp_servers list
    model="gpt-5"
)
```

#### Option D: Local Stdio Server (MCPServerStdio)

**When to use:** Server is a local script, executable, or needs to run as subprocess.

```python
import os
from pathlib import Path
from agency_swarm import Agent
from agents.mcp import MCPServerStdio

# Get the path to the local server
current_dir = Path(__file__).parent
path_to_stdio_mcp_server = current_dir / "mcp_servers" / "server-name"

# Define the stdio server
stdio_server = MCPServerStdio(
    name="Descriptive Server Name",
    params={
        "command": "uv",  # or "python", "node", "npx", etc.
        "args": [
            "--directory",
            str(path_to_stdio_mcp_server),
            "run",
            "server.py"  # Entry point from README
        ],
        "env": {
            # Pass required environment variables
            "API_KEY": os.getenv("API_KEY_NAME"),
            "ACCOUNT_ID": "your-account-id"  # if needed
        }
    },
    cache_tools_list=True,  # REQUIRED: Enable caching
    client_session_timeout_seconds=10,  # Adjust timeout as needed
    tool_filter={
        # Optional: Block specific tools you don't want to expose
        "blocked_tool_names": ["dangerous_tool", "unused_tool"]
        # Or allow only specific tools:
        # "allowed_tool_names": ["safe_tool1", "safe_tool2"]
    }
)

# Add to agent's mcp_servers parameter
agent = Agent(
    name="AgentName",
    description="Agent description",
    instructions="./instructions.md",
    mcp_servers=[stdio_server],  # Add to mcp_servers list
    model="gpt-5"
)
```

**Common command patterns for MCPServerStdio:**

```python
# NPM package (no installation needed)
params={
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "./files"]
}

# Local Python script with uv
params={
    "command": "uv",
    "args": ["--directory", str(server_path), "run", "server.py"]
}

# Local Python script with python
params={
    "command": "python",
    "args": [str(server_path / "server.py")]
}

# Local Node.js script
params={
    "command": "node",
    "args": [str(server_path / "index.js")]
}
```

#### Option E: Hosted Remote Server with OAuth (mcp-remote)

**When to use:** Server is publicly accessible but requires OAuth authentication (e.g., Notion, Google services).

This uses the `mcp-remote` tool ([documentation](https://github.com/geelen/mcp-remote)) to handle OAuth flows and token management for hosted MCP servers.

```python
import os
from pathlib import Path
from agency_swarm import Agent
from agents.mcp import MCPServerStdio

# Get the folder path to store MCP credentials locally
folder_path = Path(__file__).parent.parent  # Go up to agency root

# Define the OAuth MCP server using mcp-remote
oauth_mcp_server = MCPServerStdio(
    name="Descriptive Server Name",
    params={
        "command": "npx",
        "args": [
            "-y",
            "mcp-remote",
            "https://your-server.com/mcp"  # The hosted MCP server URL
        ],
        "env": {
            # Store OAuth credentials in ./mnt/mcp_credentials/ folder for persistence
            "MCP_REMOTE_CONFIG_DIR": os.path.join(folder_path, "mnt", "mcp_credentials")
        }
    },
    cache_tools_list=True,  # REQUIRED: Enable caching
    client_session_timeout_seconds=20,  # Increase timeout for OAuth flows
    tool_filter={
        # Optional: Limit to specific tools
        "allowed_tool_names": ["tool1", "tool2", "tool3"]
    }
)
```

**How it works:**

1. `mcp-remote` acts as a bridge between local stdio and remote OAuth servers
2. On first run, it will open a browser for OAuth authentication
3. Credentials are saved in the `mnt/mcp_credentials/` folder (don't add to `.gitignore`)
4. Subsequent runs reuse the saved tokens automatically. ./mnt folder is for persistent storage.

**Example of a Notion MCP Server:**

```python
# Notion MCP Server
notion_mcp = MCPServerStdio(
    name="Notion MCP",
    params={
        "command": "npx",
        "args": ["-y", "mcp-remote", "https://mcp.notion.com/mcp"],
        "env": {
            "MCP_REMOTE_CONFIG_DIR": os.path.join(folder_path, "mcp_credentials")
        }
    },
    cache_tools_list=True,
    client_session_timeout_seconds=20,
    tool_filter={
        "allowed_tool_names": ["notion-fetch", "notion-create-pages", "notion-update-page"]
    }
)
```

**Important Notes:**

- Increase `client_session_timeout_seconds` to at least 20 for OAuth flows
- The first run will require user interaction to authenticate
- Use `tool_filter` to limit exposed tools if needed

---

### Step 4: Add Required Environment Variables

1. Identify required API keys from server documentation
2. Add them to `.env` file:

```bash
# .env
OPENAI_API_KEY=your-key-here
API_TOKEN_NAME=your-token-here
YOUTUBE_API_KEY=your-key-here
# etc.
```

3. Ask user to fill in actual values

---

### Step 5: Update Agent Instructions

Update the agent's `instructions.md` file to provide clear, minimal guidance for using the new MCP server. Do not alter or remove existing user-written instructions—only add what is necessary to instruct the agent in referencing or using the MCP server by its name within its step-by-step process or task list. Ensure the MCP server name is explicitly mentioned in one or more steps so the agent is aware of its presence and capabilities. The agent will automatically have access to the MCP server tools and does not need to be instructed to find or import them.

---

### Step 6: Test the MCP Server Integration

Add a test block to the agent file to verify MCP tools are accessible:

```python
# At the bottom of agent_name.py file

if __name__ == "__main__":
    import asyncio

    async def test_agent():
        print("Testing MCP server integration...")

        # List available tools (should include MCP tools)
        if hasattr(agent, 'mcp_servers'):
            for server in agent.mcp_servers:
                await server.connect()
                tools = await server.list_tools()
                print(f"\nTools from {server.name}:")
                for tool in tools:
                    print(f"  - {tool.name}: {tool.description}")

        # Test with a sample message
        result = await agent.get_response("List the available tools you have access to")
        print(f"\nAgent response:\n{result.final_output}")

        # Test actual tool usage (customize based on available tools)
        # result = await agent.get_response("Use [tool_name] to [perform action]")
        # print(f"\nTool test response:\n{result.final_output}")

    asyncio.run(test_agent())
```

**Run the test:**

```bash
python agent_name/agent_name.py
```

**Expected output:**

- List of MCP tools should appear
- Agent should confirm access to the tools
- No errors about missing tools or connection issues

---

## Common MCP Server Examples

### 1. Notion Server (OAuth-authenticated Hosted)

```python
import os
from pathlib import Path
from agents.mcp import MCPServerStdio

folder_path = Path(__file__).parent.parent

notion_mcp = MCPServerStdio(
    name="Notion_MCP",
    params={
        "command": "npx",
        "args": ["-y", "mcp-remote", "https://mcp.notion.com/mcp"],
        "env": {
            "MCP_REMOTE_CONFIG_DIR": os.path.join(folder_path, "mnt", "mcp_credentials")
        }
    },
    cache_tools_list=True,
    client_session_timeout_seconds=20,
    tool_filter={
        "allowed_tool_names": ["notion-fetch", "notion-create-pages", "notion-update-page"]
    }
)
```

### 2. Filesystem Server (Local)

```python
from pathlib import Path
from agents.mcp import MCPServerStdio

samples_dir = Path(__file__).parent / "files"

filesystem_server = MCPServerStdio(
    name="Filesystem_Server",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", str(samples_dir)]
    },
    cache_tools_list=True
)
```

### 3. GitHub Server (Hosted with Token Auth)

```python
from agency_swarm import HostedMCPTool
import os

github_mcp = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "github-server",
        "server_url": "https://github-mcp-server.com/mcp/",
        "require_approval": "never",
        "headers": {
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"
        }
    }
)
```

### 4. Database Server (Local SSE)

```python
from agents.mcp import MCPServerSse
import os

db_server = MCPServerSse(
    name="Database_Server",
    params={
        "url": "http://localhost:8000/sse",
        "headers": {
            "X-Database": "production"
        }
    },
    cache_tools_list=True
)
```

---

## Tool Filtering

Limit which tools the agent can access using filters:

```python
# Block specific tools
stdio_server = MCPServerStdio(
    name="Server_Name",
    params={...},
    cache_tools_list=True,
    tool_filter={
        "blocked_tool_names": ["delete_all", "dangerous_operation"]
    }
)

# Or allow only specific tools
stdio_server = MCPServerStdio(
    name="Server_Name",
    params={...},
    cache_tools_list=True,
    tool_filter={
        "allowed_tool_names": ["read_file", "write_file", "list_files"]
    }
)
```

---

## Troubleshooting

If there is an issue, you must keep troubleshooting until the MCP server is working as expected. Common problems:

### Server won't start (MCPServerStdio)

1. Check the command is correct: `python`, `node`, `npx`, `uv`, etc.
2. Verify the path to the server exists
3. Check dependencies are installed
4. Look for error output in console
5. Try running the command manually first

### Tools not appearing

1. Verify you called `await server.connect()` (for stdio servers)
2. Check server is running (for SSE/HTTP servers)
3. Try calling `await server.list_tools()` manually
4. Check authentication headers if required

### Authentication errors

1. Verify API keys are in `.env` file
2. Ensure `.env` file is loaded with `load_dotenv()`
3. For remote MCP servers that require OAuth, use mcp-remote npm package:

```json
{
  "mcpServers": {
    "remote-example": {
      "command": "npx",
      "args": ["mcp-remote", "https://remote.mcp.server/mcp"]
    }
  }
}
```

Fetch this link for more details: https://raw.githubusercontent.com/geelen/mcp-remote/refs/heads/main/README.md

### Timeout errors

1. Increase `client_session_timeout_seconds` parameter
2. Check server is responsive
3. Verify network connectivity (for remote servers)

### OAuth / mcp-remote errors

1. **Timeout during OAuth**: Increase `client_session_timeout_seconds` to 30 or higher
2. **"Client mode" debugging**: Test connection independently:
   ```bash
   npx -y mcp-remote https://your-server.com/mcp
   ```
3. **Check logs**: Enable debug logging with `--debug` flag:
   ```python
   params={
       "command": "npx",
       "args": ["-y", "mcp-remote", "https://your-server.com/mcp", "--debug"]
   }
   ```

---

## Important Configuration Notes

1. **Always set `cache_tools_list=True`** - Required for performance
2. **HostedMCPTool uses `tools` parameter** - Not `mcp_servers`
3. **All servers except HostedMCPTool use `mcp_servers` parameter** - Not `tools`
4. **Import `load_dotenv()` and call it** - Before accessing environment variables
5. **Use descriptive server names** - Agent sees `[Server_Name].[tool_name]` format
6. **Test after adding** - Always verify tools are accessible
7. **OAuth timeout** - Set `client_session_timeout_seconds` to at least 20 for OAuth flows
8. **Allowed Tools** - `tool_filter` parameter only works when running an agent, not list_tools() method.
9. **Persistent Storage** - Use `mnt` folder for persistent storage of OAuth credentials and other data.

---

## References

- [Agency Swarm MCP Documentation](https://agency-swarm.ai/core-framework/tools/mcp-integration)
- [OpenAI Agents SDK MCP Guide](https://openai.github.io/openai-agents-python/mcp/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Servers Directory](https://github.com/modelcontextprotocol/servers)
- [mcp-remote - OAuth bridge for MCP servers](https://github.com/geelen/mcp-remote)

---

## Quick Decision Tree

```
User wants to add MCP server
│
├─ Is it a public URL?
│  ├─ Requires OAuth? → Use mcp-remote with MCPServerStdio (in mcp_servers)
│  │  ├─ Use npx -y mcp-remote <URL>
│  │  ├─ Set MCP_REMOTE_CONFIG_DIR to local folder
│  │  └─ First run opens browser for OAuth
│  └─ No OAuth? → Use HostedMCPTool (in tools parameter)
│
├─ Is it a local server URL?
│  ├─ Ends in /sse? → Use MCPServerSse (in mcp_servers)
│  └─ Ends in /mcp? → Use MCPServerStreamableHttp (in mcp_servers)
│
└─ Is it a GitHub repo or local script?
   └─ YES → Use MCPServerStdio (in mcp_servers)
      ├─ Clone repo to ./mcp_servers/<name>
      ├─ Install dependencies
      ├─ Configure command and args
      └─ Test with python agent_name.py
```
