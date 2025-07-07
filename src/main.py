import logging
from dotenv import load_dotenv

from ExampleAgency.agency import create_agency
from agency_swarm.integrations.fastapi import run_fastapi

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    run_fastapi(
        agencies={
            "ExampleAgency": create_agency,
        },
        port=8080,
        enable_agui=True,
    )
