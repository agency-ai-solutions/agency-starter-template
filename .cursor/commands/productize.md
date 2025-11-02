# Agent Productization Task

Your task is to productize an AI agent in the current repository by turning it into a reusable template. Essentially, the user wants you to ensure that he can easily customize this agent for different clients.

## Step-by-Step Process

1. Fetch the documentation for how to create onboarding forms for AI agents with our framework: https://agency-swarm.ai/platform/marketplace/onboarding Make sure to fetch the entire page.
2. Explore the current repository to understand the structure of the current agency to productize. Focus primarily on insturctions files of each agent and the shared_instructions.md file.
3. Ask the user what he would like to customize accross different clients for this agent. For example, agent name, business overview, model, output format, additional notes, etc.
4. Based on the user's answers, create a new OnboardingTool for an agent, as described in documentation. Example is provided below.
5. **Important**: When converting the agent to use an OnboardingTool, make sure to preserve existing values from the repository.
   - For each value (for example, business overview or server addresses) that you want to turn into a customizable field, do NOT overwrite or delete the user’s current data.
   - Instead, create a field for this value in the OnboardingTool, and store the existing value as the default in `onboarding_config.py`.
   - Place code that loads these defaults inside the `if __name__ == "__main__"` block of your OnboardingTool script.
   - This approach keeps the user’s current settings safe while making them configurable for future onboarding.
6. Run the onboarding_tool.py file to generate the onboarding_config.py file.
7. Import the onboarding_config.py file to customize the agent, as described in documentation.

## Example OnboardingTool

```python
from agency_swarm.tools import BaseTool
from pydantic import Field
from typing import Optional, Literal
import os
import json

class OnboardingTool(BaseTool):
    """
    Customizes the agent based on business requirements and preferences.
    Add any fields you want the user to configure during onboarding.
    """

    # Basic text field example
    company_name: str = Field(
        "Acme Corp",
        description="Your company name"
    )

    # Textarea field example (for longer text inputs)
    company_overview: str = Field(
        "A company that does amazing things.",
        description="Brief overview of your company or product",
        json_schema_extra={"ui:widget": "textarea"},
    )

    model: Literal["gpt-5", "gpt-4.1"] = Field(
        "gpt-4.1",
        description="Select the model to use: gpt-5 or gpt-4.1"
    )

    # File upload field example
    knowledge_files: list[str] = Field(
        [],
        description="Upload documentation files for the agent to reference.",
        json_schema_extra={
            "x-file-upload-path": "./agent_name/files",  # Replace with your agent folder. FIles will be automatically uploaded to this path.
        },
    )

    # Add more fields as needed:
    # - Use str for text inputs
    # - Use Optional[str] for optional inputs
    # - Use list[str] for file uploads
    # - Add json_schema_extra={"ui:widget": "textarea"} for multi-line text
    # - Add json_schema_extra={"ui:placeholder": "placeholder"} for field placeholder text
    # - Add json_schema_extra={"x-file-upload-path": "./path"} for file uploads

    def run(self):
        """Saves configuration to onboarding_config.py"""
        # Get the directory where this tool is located
        tool_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(tool_dir, "onboarding_config.py")

        # Convert tool fields to dictionary
        config = self.model_dump()

        # Convert to Python code format
        json_str = json.dumps(config, indent=4)
        json_str = json_str.replace(': null', ': None').replace(': true', ': True').replace(': false', ': False')
        python_code = f"# Auto-generated configuration\n\nconfig = {json_str}\n"

        # Write to file
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(python_code)

        return f"Configuration saved to {config_path}"

# Test the tool
if __name__ == "__main__":
    tool = OnboardingTool(
        company_name="Test Company",
        company_overview="This is a test.",
        support_email="support@test.com"
    )
    print(tool.run())
```

**Key Points:**

- Each field becomes a form input in the onboarding UI
- Use clear descriptions - they become field labels/help text
- The `run()` method saves all fields to `onboarding_config.py`
- Import the config in your agent's instructions or tools with: `from .tools.onboarding_config import config`

## Example Usage

After running the OnboardingTool, use the generated config in your agent:

```python
from agency_swarm import Agent
from .tools.onboarding_config import config
import os

# Option 1: Use config values directly in agent initialization
my_agent = Agent(
    name=config["company_name"] + " Assistant",
    description="Helps with customer inquiries",
    instructions="./instructions.md",
    files_folder="./files",
    model="gpt-5"
)

# Option 2: Dynamically render instructions with config values
def render_instructions():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    instructions_path = os.path.join(current_dir, "instructions.md")

    with open(instructions_path, "r") as file:
        instructions = file.read()

    # Use Python's format() to inject config values into instructions
    instructions = instructions.format(
        company_name=config["company_name"],
        company_overview=config["company_overview"],
        support_email=config.get("support_email", "N/A")
    )

    return instructions

my_agent = Agent(
    name="Support Agent",
    description="Customer support assistant",
    instructions=render_instructions(),  # Dynamic instructions
    files_folder="./files",
    model=config["model"], # example how to customize the model.
)
```

In your `instructions.md` file, use placeholders:

```markdown
# Role

You are a customer support agent for {company_name}.

# Company Overview

{company_overview}

# Contact Information

For escalations, contact: {support_email}
```

## Best Tips & Practices

- Handle None values gracefully in your code. If the field is optional, use the `get` method to get the value, and provide a default value if the value is None.
