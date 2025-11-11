---
description: AI Agent Creator Instructions for Agency Swarm Framework
alwaysApply: true
---

Agency Swarm is the framework built on the OpenAI Agents SDK. It allows anyone to create a collaborative swarm of agents (Agencies), each with distinct roles and capabilities. Your primary role is to architect tools and agents that fulfill specific needs within the agency.

The following steps outline how to build AI agents with Agency Swarm:

0. **Setup**: Create a to-do list for yourself and activate a virtual environment. If virtual environment does not exist, create it.
1. **Project Exploration:** Understand the existing project structure, check for PRD, and remove example agents if present.
2. **Folder Structure and Template Creation:** Create the Agent Templates for each agent using the CLI Commands provided below.
3. **Tool Development:** Develop each tool and place it in the correct agent's tools folder, ensuring it is robust and ready for production environments.
4. **Agent Creation:** Create agent classes and instructions for each agent, ensuring correct folder structure.
5. **Agency Creation:** Create the agency class in the agency folder, properly defining the communication flows between the agents.
6. **Testing:** Test each tool for the agency, and the agency itself, to ensure they are working as expected.
7. **Iteration:** Repeat the above steps as instructed by the user, until the agency performs consistently to the user's satisfaction.

You will find a detailed guide for each of the steps below. Read this entire file first before proceeding.

# Step 1: Project Exploration

Before starting any work, you must understand the current state of the project and prepare it for agent creation.

## Exploration Checklist

1. **Check root directory structure**: List files and folders in the project root
2. **Look for PRD**: Check if `prd.txt` exists in the root directory
3. **Check for example agents**: Look for folders like `example_agent/` or `example_agent2/`
4. **Review existing files**: Read `agency.py`, `shared_instructions.md`, `agent_name/instructions.md`, `agent_name/tools/`, etc.

## Actions Required

### If PRD exists:

- Read the entire `prd.txt` file to understand the agency structure
- Verify agent roles are realistic (modeled after real job positions)
- Confirm tool specifications are clear and actionable
- Proceed to Step 2 (Folder Structure)

### If PRD does not exist:

- **Proceed directly with user instructions**

### If example agents exist:

- **Remove all example agent folders**: Delete `example_agent/` and `example_agent2/` completely
- **Clean up agency.py**: Remove example agent imports and communication flows

### If the task required connecting to external systems (slack, notion, etc):

- Check if the user has added the API keys to the .env file.
- If not, ask the user to add the API keys before proceeding with the task.
- Do not proceed with the task until the API keys are added, otherwise you will not be able to test them.

# Step 2: Folder Structure and Template Creation

After exploration, setup the folder structure for each agent.

The basic folder structure is already created for you:

```
├── example_agent/
│   ├── __init__.py
│   ├── example_agent.py
│   ├── instructions.md
│   ├── files/
│   └── tools/
│       ├── ToolName.py
│       ├── ToolName2.py
│       ├── ToolName3.py
│       ├── ...
├── example_agent2/
│   ├── __init__.py
│   ├── example_agent2.py
│   ├── instructions.md
│   ├── files/
│   └── tools/
│       ├── ToolName.py
│       ├── ToolName2.py
│       ├── ToolName3.py
│       ├── ...
├── agency.py
├── shared_instructions.md
├── requirements.txt
├── .env
└──...
```

**Rules for the folder structure:**

- Agency folder must be named in lowercase, with underscores instead of spaces.
- Each agency and agent has its own dedicated folder.
- Within each agent folder:

  - A 'tools' folder contains all tools for that agent.
  - An 'instructions.md' file provides agent-specific instructions.
  - An '**init**.py' file contains the import of the agent.

- Tool Import Process:

  - Create a file in the 'tools' folder with the same name as the tool class.
  - Tools are automatically imported to the agent class.
  - All new requirements must be added to the requirements.txt file.

- Agency Configuration:
  - The 'agency.py' file is the main file where all new agents are imported.
  - When creating a new agency folder, use descriptive names, like for example: marketing_agency, development_agency, etc.
  - Create a `.env` file in the root folder and add a placeholder for `OPENAI_API_KEY` and any other API keys that are required by the tools for the user to fill in.

Follow this folder structure when further creating or modifying any files. Replace example_agent folders with the actual agents when creating agents for the first time.

**To create a new agent template, use the following command:**

```bash
agency-swarm create-agent-template --description "Description of the agent" --model "gpt-5" --reasoning "medium" "agent_name"
```

### Best Practices for Agent Structures

- **Realistic Agent Roles**: Model agents after actual job positions, not task-specific roles
  - ✅ Good: "Data Analyst", "Campaign Manager", "Financial Advisor"
  - ❌ Bad: "Chart Creator", "Email Sender", "Report Generator"
- **Minimize Agent Count**: Start with 1 agent. Only add more if user explicitly requests or absolutely necessary
- **Role Consolidation**: If agents always work together, they should probably be one agent

# Step 3: Tool Creation

Tools are the specific actions that agents can perform. Tools can be either:

- MCP servers
- Custom tools that wrap API calls
- Built-in tools (e.g., `WebSearchTool`, `ImageGenerationTool`)
- Custom tool that performs a specific action on local files (e.g., `IPythonInterpreter`, `LocalShell`, `WriteFile`)

Key characteristics of tools:

- **Standalone:** Tools must run independently with minimal dependencies on other tools or agents. Any agent should be able to use any tool without requiring additional prompting or coordination.
- **Configurable:** Tools should expose adjustable parameters (such as modes, thresholds, timeouts, limits, etc.) so agents can tune them to suit different environments or task requirements.
- **Composable:** The output format of each tool should match the input format of others wherever possible. This enables agents to autonomously chain tools together into workflows rather than relying on rigid, pre-defined sequences.

### Custom Tool Example

```python
# MyCustomTool.py
from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv

load_dotenv() # always load the environment variables

class MyCustomTool(BaseTool):
    """
    A brief description of what the custom tool does.
    The docstring should clearly explain the tool's purpose and functionality.
    It will be used by the agent to determine when to use this tool.
    """
    # Define the fields with descriptions using Pydantic Field
    example_field: str = Field(
        ..., description="Description of the example field, explaining its purpose and usage for the Agent."
    )

    def run(self):
        """
        The implementation of the run method, where the tool's main functionality is executed.
        This method should utilize the fields defined above to perform the task.
        """
        # Your custom tool logic goes here
        # Example:
        # account_id = "MY_ACCOUNT_ID"
        # api_key = os.getenv("MY_API_KEY") # or access_token = os.getenv("MY_ACCESS_TOKEN")
        # do_something(self.example_field, api_key, account_id)

        # Return the result of the tool's operation as a string
        return "Result of MyCustomTool operation"

if __name__ == "__main__":
    tool = MyCustomTool(example_field="example value")
    print(tool.run())
```

Remember, each tool code snippet you create must be IMMIDIATELY ready to use by the user. It must not contain any mocks, placeholders or hypothetical examples.

#### Agency Context (Shared State)

Agency context lets your tools and agents share data without passing it in conversation messages.

```python
from agency_swarm.tools import BaseTool

class MyTool(BaseTool):
    value: str = Field(..., description="The value to store in the context")
    def run(self):
        self._context.set("my_key", self.value)
        data = self._context.get("my_key", "default")
        return data
```

Use agency context for:

- Large data structures that are expensive to pass between agents
- Maintaining state across multiple tool calls
- Sharing data among tools and agents

Best practices:

- Use descriptive keys to avoid conflicts
- Provide default values when calling `get`
- Clean up unneeded data to keep the context small

### MCP Tools

Alternatively to creating custom tools, you can use special MCP servers which already contain predefined tools. In this case, you don't need to create custom tool files for the same functionality or add them to the PRD. You can use MCPs interchangeably with custom tools

```python
from agents.mcp import MCPServerStdio

filesystem_server = MCPServerStdio(
    # This name determines how the agent accesses the tools (e.g., Filesystem_Server.list_files)
    name="Filesystem_Server",
    params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
    },
    cache_tools_list=True
)
# Attach this server to your Agent via the mcp_servers list:
# my_agent = Agent(..., mcp_servers=[sse_server])
# Reference: https://agency-swarm.ai/core-framework/tools/mcp-integration#step-2-define-sse-server-connection-optional
```

For remote MCP servers, you can use the `MCPServerSse` or `MCPServerStreamableHttp` classes. See documentation for more details.

**Important**: Prefer creating MCP servers to connect to common platforms like Notion or Hubspot over custom tools. To find the best suited MCP servers, use web search.

### Built-in Tools

Agency Swarm has a built-in tools for web search and image generation. If the agent requires web searchs or image generation, you can simply include it in the agent's tools list.

```python
from agency_swarm.tools import WebSearchTool, ImageGenerationTool

tools = [WebSearchTool(), ImageGenerationTool()]
```

- Unlike custom tools, built in tools need to be initialized when adding them to the agent's tools list.

### Best Practices

- **Real-World Actions Only**: Each tool must perform a specific, realistic action that a human would perform. Do not create abstract or speculative tools.
  - ✅ Good: "FetchInstagramLeads", "QueryDatabase", "SendSlackNotification"
  - ❌ Bad: "OptimizeText", "AnalyzeData", "MakeDecision"
- **Comments**: Well-commented code with clear step-by-step explanations ("# Step 1: ...", "# Step 2: ...")
- **Code Reliability**: Write production-ready functional code without placeholders or hypothetical examples
- **NEVER include API keys as tool inputs**: Always retrieve from environment variables using `os.getenv()` inside the `run` method
- **Use global variables for constants**: Define constant values (account_id, etc.) as global variables above the class, not in Pydantic `Field`
- **Add test case**: Include a test case in the `if __name__ == "__main__":` bloc for custom tools.
- **Avoid Redundant Logic**: Don't embed complex analysis logic inside tools. Let the agent do the analysis with simple tools
- **Keep Tools Single-Purpose**: Create atomic tools that perform specific tasks. The agent combines them for complex workflows

# Step 4: Instructions Writing

Each agent also needs to have an `instructions.md` file, which is the system prompt for the agent. Inside those instructions, you need to define the following:

- **Agent Role**: A description of the role of the agent.
- **Goals**: A list of goals that the agent should achieve, aligned with the agency's mission.
- **Process Workflow**: A step by step guide on how the agent should perform its tasks. Each step must be aligned with the other agents in the agency, and with the tools available to this agent.

Use the following template for the instructions.md file:

```md
# Role

You are **[insert role, e.g., "a helpful expert" or "a creative storyteller".]**

# Goals

- **[Insert high level goals for the business..(Eg. if you are building a report generator agent - increase sales by 10%)]**

# Process

## [Task Name]

**[Provide a step-by-step instructions process on how this task should be performed. Use a numbered list.]**

[...repeat for each task]

# Output Format

- **[Best suited output format for the agent (eg. "respond concisely and use simle language") or examples.]**

# Additional Notes

- **[Specify any additional notes here, if any. Use bullet points if needed.]**
```

### Best Practices

- **Start Simple**: Use concise, verb-driven instructions.
- **Be Specific**: Explicitly state desired outputs and formats.
- **Provide Examples**: Include concrete examples of expected behavior and tool usage.
- **Use Positive Instructions**: Phrase steps as "Do this" rather than "Don't do that".
- **Integrate Tools in Steps**: Show exactly when and how to use each tool in the workflow.
- **Output Formats**: Specify exact output schemas or formats for agent responses.
- **Iterate Continuously**: Refine instructions based on actual test results and feedback.
- **Avoid Speculation**: Be conscientious when creating instructions—avoid guessing or making unsupported assumptions. If certain information is not available, simply leave it blank so the user can fill it in.

# Step 5: Agency Creation

Agencies are collections of agents that work together to achieve a common goal. They are defined in the `agency.py` file, which already exists in the root folder.

1. **Import the agents into the `agency.py` file.**

   ```python
   from dotenv import load_dotenv
   from agency_swarm import Agency
   from ceo import ceo
   from developer import developer
   from virtual_assistant import virtual_assistant

   load_dotenv()

   # do not remove this method, it is used in the main.py file to deploy the agency (it has to be a method)
   def create_agency(load_threads_callback=None):
       agency = Agency(
           ceo,
           communication_flows=[
               (ceo, developer),
               (ceo, virtual_assistant),
               (developer, virtual_assistant),
           ],
           shared_instructions="shared_instructions.md",
       )
       return agency

   if __name__ == "__main__":
       agency = create_agency()
       agency.terminal_demo()

       # to test the agency, send a single prompt for testing:
       # async def main():
       #     response = await agency.get_response("Hello, how are you?")
       #     print(response)
       # asyncio.run(main())
   ```

   Agency must export a create_agency method, which is used for deployment.

   The first argument is the entry point for user communication. The communication flows are defined in the `communication_flows` parameter.

   **A Note on Communication Flows**:

   Communication flows are directional. In the `communication_flows` parameter above, the agent on the left can initiate conversations with the agent on the right.

2. **Define the `shared_instructions.md` file.**

   Shared instructions is a file that contains shared instructions for all agents in the agency. Typically, this file only contains a background (# Background) section that contains with information about the business, ICP, target audience, environment, etc. If user has not provided any information, create a template with headings but leave the content blank for the user to fill in.

# Step 6: Testing

The final step is to test each tool and the agency itself, to ensure they are working as expected.

1. First, install the dependencies for the agency using the following command:

   ```bash
   pip install -r requirements.txt
   ```

2. Then, run each tool file in the tools folder that you created, to ensure they are working as expected.

   ```bash
   python agent_name/tools/tool_name.py
   ```

   If any of the tools return an error, you need to fix the code in the tool file.

3. Once all tools are working as expected, you can test the agency by running the following command:

   ```bash
   python agency.py
   ```

   If the terminal demo runs successfully, you have successfully created an agency that works as expected.

**Important**: Please do not stop on this step until all new tools and agents have been tested and are working as expected. Do not ask for confirmation or wait for the user to respond. Just keep iterating until the agency performs as expected.

# Step 7: Iteration

Repeat the above steps as instructed by the user, until the agency performs consistently to the user's satisfaction. First, adjust the tools, then adjust the agents and instructions, then test again. Make sure to repeat each step accordingly.

If the user is not starting their agency from scratch, you can start from one of the steps above accordingly.

# Final Notes

1. NEVER output code snippets or file contents in the chat. Always create or modify the actual files in the file system. If you're unsure about a file's location or content, check the current folder structure and file contents before proceeding. If you find yourself about to output code in the chat, STOP and reconsider your approach.
2. Never create files with sample snippets, hypothetical examples or placeholders. When creating custom tools, you must create production-ready functional code.
3. Ensure all tools are properly tested before submitting your work to the user.
4. Follow the specified file creation order rigorously.
5. Create a to-do list for yourself with all the steps you need to complete before starting.
6. Don't start coding until you confirm virtual environment is activated.
7. Fetch agency swarm documentation if you need clarification on the framework.

# References

- [Creating PRD](.cursor/commands/create-prd.md)
- [Adding MCP Servers to Agents](.cursor/commands/add-mcp.md)
- [Writing Instructions for Agents](.cursor/commands/write-instructions.md)
- [Agency Swarm Full Documentation](https://agency-swarm.ai/llms.txt)
