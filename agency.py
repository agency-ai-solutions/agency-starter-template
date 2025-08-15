from dotenv import load_dotenv
from agency_swarm import Agency

from ExampleAgency.ExampleAgent.ExampleAgent import ExampleAgent
from ExampleAgency.ExampleAgent2.ExampleAgent2 import ExampleAgent2

import asyncio

load_dotenv()

# do not remove this method, agency.py **must** expose a create_agency method
# this method is used on the server to deploy the agency
def create_agency(load_threads_callback=None):
    agent = ExampleAgent()
    agent2 = ExampleAgent2()
    agency = Agency(
        agent, agent2,
        communication_flows=[(agent, agent2)],
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