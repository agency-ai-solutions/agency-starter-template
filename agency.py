from dotenv import load_dotenv
from agency_swarm import Agency

from ExampleAgency.ExampleAgent.ExampleAgent import ExampleAgent
from ExampleAgency.ExampleAgent2.ExampleAgent2 import ExampleAgent2
from ExampleAgency.DatabaseAnalysisAgent.DatabaseAnalysisAgent import DatabaseAnalysisAgent

import asyncio

load_dotenv()

def create_agency(load_threads_callback=None):
    agent = ExampleAgent()
    agent2 = ExampleAgent2()
    db_agent = DatabaseAnalysisAgent()
    agency = Agency(
        db_agent, agent, agent2,
        communication_flows=[(db_agent, agent), (agent, agent2), (db_agent, agent2)],
        shared_instructions="agency_manifesto.md",
        load_threads_callback=load_threads_callback,
    )

    return agency

if __name__ == "__main__":
    agency = create_agency()

    # test 1 message
    # async def main():
    #     response = await agency.get_response("Hello, how are you?")
    #     print(response)
    # asyncio.run(main())

    # run in terminal
    agency.terminal_demo()