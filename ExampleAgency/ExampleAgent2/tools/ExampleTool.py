from agency_swarm.tools import BaseTool
from pydantic import Field
import os
from dotenv import load_dotenv

load_dotenv()

class ExampleTool(BaseTool):
    """
    A tool that provides a simple greeting message with customization options.
    This tool can be used to generate personalized greetings for users.
    """

    name: str = Field(
        ...,
        description="The name of the person to greet.",
    )
    
    greeting_type: str = Field(
        default="Hello",
        description="The type of greeting to use (e.g., Hello, Hi, Greetings).",
    )

    def run(self):
        """
        Generates a personalized greeting message.
        """
        greeting = f"{self.greeting_type}, {self.name}!"
        return greeting


if __name__ == "__main__":
    # Test the tool with different inputs
    tool = ExampleTool(name="John", greeting_type="Hi")
    print(tool.run())  # Should print: "Hi, John!"
