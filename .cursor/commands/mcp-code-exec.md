# MCP Code Execution Pattern - Implementation Guide

Your task is to convert an MCP server into the **Code Execution Pattern** described in [Anthropic's blog post](https://www.anthropic.com/engineering/code-execution-with-mcp). This pattern enables **progressive disclosure** of tools, reducing token usage by up to 98% compared to loading all tools upfront.

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

## Step-by-Step Implementation

### Step 0: Create a TO-DO List.

Before starting, check if the user has provided the necessary auth credentials for the MCP servers. If not, ask the user to provide them before starting this task.

After credentials are provided, create a to-do list for yourself with all the steps you need to complete below.

### Step 1: Create MCP Server Files

Create a dedicated folder for the MCP server in `./agent_name/mcp_servers/` directory.

**Example:**

```
./agent_name/mcp_servers/[server_name]/
├── notion.py           # Server singleton & connection management (with discovery in __main__)
├── salesforce.py
├── github.py
├── youtube.py
└── __init__.py         # Package exports
```

### Step 2: Create the Server Module

The `server.py` module manages the MCP server connection as a singleton. It is converted into tools using `ToolFactory.from_mcp` method, available in agency_swarm specifically for this pattern. This method converts the MCP server into a list of tools.

Include tool discovery in the `__main__` block to list available tools.

**Note:** This pattern works with any MCP server type, except HostedMCPTool. The template below shows `MCPServerStdio` (most common), but you can use:

- `MCPServerStdio` - Local scripts, npm packages, or OAuth servers with `mcp-remote`
- `MCPServerSse` - Server-Sent Events servers
- `MCPServerStreamableHttp` - HTTP streaming servers

See `.cursor/commands/add-mcp.md` for detailed configuration of each server type.

**Template (`./agent_name/mcp_servers/[server_name].py`):**

```python
"""[Server Name] MCP Server Configuration"""
from agency_swarm.tools import ToolFactory
# Choose the appropriate import based on your server type:
from agents.mcp import MCPServerStdio  # For local scripts, npm packages, or mcp-remote
# from agents.mcp import MCPServerSse  # For Server-Sent Events servers
# from agents.mcp import MCPServerStreamableHttp  # For HTTP streaming servers

import os

server_name_mcp = MCPServerStdio( # replace server_name with the name of the MCP server like notion_mcp, salesforce_mcp, github_mcp, youtube_mcp, etc.
    name="[server_name]_mcp",
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
# server_name_mcp = MCPServerSse(
#     name="[server_name]_mcp",
#     params={
#         "url": "http://localhost:8000/sse",
#         "headers": {"Authorization": f"Bearer {os.getenv('API_TOKEN')}"}
#     },
#     cache_tools_list=True
# )

# Example: Remote OAuth server
# server_name_mcp = MCPServerStdio(
#     name="[server_name]_mcp",
#     params={
#         "command": "npx",
#         "args": ["-y", "mcp-remote", "https://your-server.com/mcp"],
#         "env": {
#             "MCP_REMOTE_CONFIG_DIR": os.path.join(folder_path, "mnt", "mcp-creds") # persistent storage for OAuth credentials, don't add to .gitignore
#         }
#     },
#     cache_tools_list=True,
#     client_session_timeout_seconds=30
# )

tools = ToolFactory.from_mcp([server_name_mcp])

def generate_schema_file():
    """Generate readable text schema file for agent's file_search."""
    lines = ["[SERVER_NAME] MCP TOOLS", "", "Server: [server_name]_mcp",
             "Description: MCP server description here",
             f"Total Tools: {len(tools)}", ""]

    for idx, tool in enumerate(tools, 1):
        lines.extend(["", f"TOOL {idx}: {tool.name}", "", f"Description:", f"  {tool.description}", "", f"Parameters:"])
        params = tool.params_json_schema
        props = params.get("properties", {})
        required = params.get("required", [])

        if props:
            for name, info in props.items():
                req = "(required)" if name in required else "(optional)"
                lines.extend([f"  - {name} {req}", f"    Type: {info.get('type', 'any')}",
                            f"    Description: {info.get('description', 'No description')}"])
        else:
            lines.append("  No parameters required")
        lines.append("")

    agent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_path = os.path.join(agent_folder, "files", "[server_name]_mcp.txt")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"✓ Generated schema file: {output_path}")
    print(f"✓ Contains {len(tools)} tools")
    return output_path

if __name__ == "__main__":
    generate_schema_file()
```

**Run to generate schema file:**

```bash
python ./agent_name/mcp_servers/[server_name]_mcp.py
```

This will create a JSON schema file in the agent's `files` folder that the agent can search using natural language.

**Notes**:

- Make sure not to create an extra files folder. When creating a json schema, it must be saved in the same files folder that might already exist.
- Each schema file must be a .txt file, not a .json file.

### Step 3: Generate Schema File

Generate the JSON schema file for the agent's knowledge base by running the MCP server file:

```bash
python ./agent_name/mcp_servers/[server_name]_mcp.py
```

This creates `agent_name/files/[server_name]_mcp.txt` containing all tool schemas in a readable text format that the agent can search.

### Step 4: Test Individual Tools

Test the individual tools from the list to confirm the server is working by invoking them directly in terminal.

**How to invoke an MCP tool:**

```python
python -c "
import asyncio
import json
from agent_name.mcp_servers.server_name_mcp import tools

async def test():
    tool = tools[0]
    result = await tool.on_invoke_tool(None, json.dumps({}))
    print(result)

asyncio.run(test())
"
```

**Example - Testing list_allowed_directories:**

```python
python -c "
import asyncio
from example_agent.mcp_servers.filesystem_mcp import tools

async def test():
    tool = [t for t in tools if t.name == 'list_allowed_directories'][0]
    result = await tool.on_invoke_tool(None, '{}')
    print(result)

asyncio.run(test())
"
```

**Note**: Only execute read-only tools (list, read, get, search). Do not update or create any data.

**Do not come back to the user until you have actually invoked at least 1 tool for each MCP server.**

### Step 5: Add the necessary tools to the agent

To allow the agent to use this new pattern, it needs to have both PersistentShellTool and IPythonInterpreter tools. Make sure to add them to the agent's tools list:

```python
from agency_swarm.tools import PersistentShellTool, IPythonInterpreter, FileSearchTool
from agency_swarm import Agent
from agents import ModelSettings
from openai.types.shared import Reasoning

agent_name = Agent(
    name="AgentName",
    description="Agent description",
    instructions="./instructions.md",
    tools=[PersistentShellTool, IPythonInterpreter], # add to tools list
    files_folder="./files", # make sure toadd to files folder
    model="gpt-5",
    model_settings=ModelSettings(
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)
```

Additionally, don't forget to set the `files_folder` to "./files" which points to the files folder in the agent's directory.

### Step 6: Add Extra Packages

To `requirements.txt`, add the following packages:

```
nest_asyncio
agency_swarm[jupyter]
```

After that, install the requirements using the following command:

```bash
pip install -U -r requirements.txt
```

**Important**: Make sure venv is activated before installing the requirements. If not, check if it exists and activate or create it first.

### Step 7: Update instructions.md

Update instructions.md for the agent to use the file_search approach. The agent should:

1. **Search for tools** using natural language queries in their knowledge base (files folder)
2. **Load and invoke** only the specific tools needed

**Example instructions section:**

````markdown
## Using MCP Tools

When you need to access MCP tools:

1. Search for relevant tools using natural language queries in your knowledge base by using `file_search` tool
2. Once you find the tool and its parameter definitions, load and invoke it using `IPythonInterpreter`:

   ```python
   import json
   from agent_name.mcp_servers.server_name_mcp import tools

   # Find tool by name from search results
   tool = [t for t in tools if t.name == 'tool_name'][0]

   # Invoke it (use await directly, not asyncio.run)
   result = await tool.on_invoke_tool(None, json.dumps({"param": "value"}))

   # Parse the result - MCP returns {"type": "text", "text": "actual content"}
   result_data = json.loads(result)
   content = result_data["text"]
   print(content)
   ```
````

- Make sure to replace server_name and agent_name with the actual server name and agent name in real instructions.
- Keep instructions minimal. Agent discovers tools autonomously via search. Prefer editing existing instructions over creating new ones.
- Read `.cursor/commands/write-instructions.md` for more details on effective agent instructions.
- Put the instructions where it makes the most sense in the current instructions.md file. Read it first.

## Troubleshooting

### OAuth timeout (Important!)

**Symptom**: `McpError: Timed out while waiting for response`

**Fix**: Increase `client_session_timeout_seconds` to 30 or higher in server.py

### User can't authenticate on deployed server

**Symptom**: MCP server can't authenticate when agency is deployed.

**Fix**:

1. Ensure `MCP_REMOTE_CONFIG_DIR` is set correctly for mcp-remote servers.
2. Ensure all other MCP servers store credentials in `./mnt/mcp-creds`.
3. Do not add credentials to .gitignore or .dockerignore. Instead, tell the user to ensure their repo is not public.
4. Make sure to add node install to Dockerfile if using any npm servers, like mcp-remote.

### Agent Can't Discover The Tools in File Search

**Symptom**: Agent tries to check tools manually in code by listing the tools in the `tools` list.

**Fix**:

1. Ensure only 1 files folder is created. When creating a json schema, it must be saved in the same files folder that might already exist.
2.

## References

- [Anthropic: Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)
- [Agency Swarm MCP Integration](https://agency-swarm.ai/core-framework/tools/mcp-integration)
- [Adding MCP Servers to Agents](.cursor/commands/add-mcp.md)
- [Writing Instructions for Agents](.cursor/commands/write-instructions.md)

## Final Notes

- If credentials for testing are missing, notify the user to provide them before starting this task.
- YOU MUST NEVER SKIP THE TEST. NEVER RUN A DUMMY TEST CASE WITH ONLY PRINT STATEMENTS OR IMPORTS. TEST AT LEAST 1 TOOL FOR EACH SERVER. ASK THE USER TO PROVIDE THE CREDENTIALS IF NEEDED.
- DO NOT tell the user the task has been completed until you have tested at least 1 tool for each MCP server.
- Test tools by running python in terminal using source `venv/bin/activate && python -c "<your test code>"`, instead of creating local python files.
