import logging
from dotenv import load_dotenv

from ExampleAgency.agency import create_agency
from agency_swarm.integrations.fastapi import run_fastapi

from agents import RunContextWrapper, function_tool

from agency_swarm import Agency, Agent

from agency_swarm.ui.demos.launcher import CopilotDemoLauncher

load_dotenv()

if __name__ == "__main__":
    """Launch interactive Copilot demo"""
    print("🚀 Agency Swarm Copilot Demo")
    print("=" * 50)
    print()

    try:
        agency = create_agency()
        # Launch the Copilot UI demo with backend and frontend servers.
        launcher = CopilotDemoLauncher()
        launcher.start(agency)

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()
