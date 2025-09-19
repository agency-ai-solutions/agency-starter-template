from agents import ModelSettings
from agency_swarm import Agent
from openai.types.shared import Reasoning

example_agent2 = Agent(
    name="ExampleAgent2",
    description="A helpful and knowledgeable assistant that provides comprehensive support and guidance across various domains.",
    instructions="./instructions.md",
    tools_folder="./tools",
    model="gpt-5",
    model_settings=ModelSettings(
        max_tokens=25000,
        reasoning=Reasoning(
            effort="medium",
            summary="auto",
        ),
    ),
)

