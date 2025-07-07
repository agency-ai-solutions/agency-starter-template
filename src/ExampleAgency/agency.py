from dotenv import load_dotenv
from agency_swarm import Agency

from ExampleAgency.ExampleAgent.ExampleAgent import ExampleAgent
from ExampleAgency.ExampleAgent2.ExampleAgent2 import ExampleAgent2

load_dotenv()

def create_agency(load_threads_callback=None) -> Agency:
    agent = ExampleAgent()
    agent2 = ExampleAgent2()
    return Agency(
        agent,
        agent2,
        communication_flows=[(agent, agent2)],
        load_threads_callback=load_threads_callback,
        shared_instructions="agency_manifesto.md",
    )
