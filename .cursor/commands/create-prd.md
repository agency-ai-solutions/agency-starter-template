# PRD Creation - Product Requirements Document for Agency Swarm

Your task is to create a Product Requirements Document (PRD) that defines the agency structure, agent roles, and tool specifications.

---

## Step 1: Ask Questions

Ask the user for:

- **Agency Name**
- **Purpose**: What does the agency do?
- **Agent Roles**: What roles are needed?
- **Communication Flows**: How do agents communicate?
- **Tools per Agent**: What actions should each agent perform?
- **External Integrations**: What APIs or services will be used?

---

## Step 2: Research

Search for available MCP servers for the systems user wants to connect to.

**MCP Search Priority:**

1. Check official registry: https://github.com/mcp
2. Search using web search: `mcp server <system name>`
3. If not MCP server is found, search for API documentation and create a custom tool that wraps the API call.

**Common MCP Servers:**

- `@modelcontextprotocol/server-filesystem` - File operations
- `@modelcontextprotocol/server-github` - GitHub
- `@modelcontextprotocol/server-slack` - Slack
- `@modelcontextprotocol/server-postgres` - PostgreSQL
- `@modelcontextprotocol/server-sqlite` - SQLite
- `@modelcontextprotocol/server-puppeteer` - Web automation
- `@modelcontextprotocol/server-brave-search` - Web search

**Built-in Tools:**

- `WebSearchTool` - Built-in web search (use this instead of MCP for web search)

**For each integration:**

- Document MCP server package name if found
- Note required API keys and how to obtain them
- If no MCP exists, note that custom tool will be needed

---

## Step 3: Create PRD

Create `./prd.txt` using this template:

```md
# [Agency Name]

---

- **Purpose:** [High-level description: what the agency achieves, target market, value proposition]

- **Communication Flows:**
  - **Between Agents:**
    - [Description of protocols and flows between agents, shared resources, data exchange]
    - **Example Flow:**
      - **[Agent A] -> [Agent B]:** [Trigger conditions, interaction description, expected outcomes]
      - **[Agent B] -> [Agent C]:** [Trigger conditions, interaction description, expected outcomes]
  - **Agent to User Communication:** [How agents communicate with users, interfaces, channels]

---

## [Agent Name]

### Role within the Agency

[Description of realistic job role and responsibilities - model after actual professions]

### Tools

- **[ToolName]:**
  - **Description**: [What this tool does and when it's used - must be a real-world task]
  - **Inputs**:
    - [name] (type) - description
  - **Validation**:
    - [Condition] - description
  - **Core Functions:** [Main functions the tool performs]
  - **APIs**: [List of APIs used, if any]
  - **Output**: [Expected output format - string or JSON object]
- **MCP Name**: [MCP server package name if found]
  - **URL**: [Url of the server’s github / official page]
  - **Authentication**: [How the MCP is authenticated]
  - **Allowed Tools**: [Which tools to allow]

---

[...repeat for each agent]
```

---

## Best Practices

**Agent Design:**

- Start with 1 agent
- Only add more if user explicitly requests
- Model after real jobs: "Data Analyst" ✅, not "Chart Creator" ❌

**Tool Design Best Practices:**

Each tool should perform one simple, human-like action (e.g., "FetchInstagramLeads" ✅, not "OptimizeText" ❌). Key characteristics of tools:

- **Standalone:** Tools must run independently with minimal dependencies on other tools or agents. Any agent should be able to use any tool without requiring additional prompting or coordination.
- **Configurable:** Tools should expose adjustable parameters (such as modes, thresholds, timeouts, limits, etc.) so agents can tune them to suit different environments or task requirements.
- **Composable:** The output format of each tool should match the input format of others wherever possible. This enables agents to autonomously chain tools together into workflows rather than relying on rigid, pre-defined sequences.

Tools can be either:

- MCP server
- Custom tool that wraps an API call
- Built-in tool (e.g., `WebSearchTool`)
- Custom tool that performs a specific action on local files (e.g., `IPythonInterpreter`, `LocalShell`, `WriteFile`)

**API Requirements:**

- List all required API keys for `.env.template` file
- Prefer MCP servers for common platforms
- If no MCP server is found, create a custom tool that wraps an API call.

---

## References

- [Agency Swarm Documentation](https://agency-swarm.ai/llms.txt)
- [Workflow Guide](.cursor/rules/workflow.mdc)
