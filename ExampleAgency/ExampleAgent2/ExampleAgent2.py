from agency_swarm import Agent


class ExampleAgent2(Agent):
    def __init__(self):
        super().__init__(
            name="ExampleAgent2",
            description="A helpful and knowledgeable assistant that provides comprehensive support and guidance across various domains.",
            instructions="./instructions.md",
            tools_folder="./tools",
            model="gpt-4o",
        )

