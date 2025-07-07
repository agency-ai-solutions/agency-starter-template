# Agency Swarm GitHub App Deployment Template

This repo demonstrates how to build any Agency Swarm agency as a FastAPI application with AG-UI protocol in a Docker container and deploy it via GitHub App.

<!-- **Video resource:** -->

---

## Prerequisites

- A fully tested Agency Swarm agency
- Docker installed (optional for local testing)
- Python 3.12
- OpenAI API key

## Setup Instructions

1. **Configure environment variables:**
   - Copy `.env.example` to `.env` and add your environment variables.

2. **Add requirements:** Add your extra requirements to the `requirements.txt` file.

3. **Add your Agency:**
   Drag-and-drop your agency into the `/src` directory and import it according to the example in `main.py` and `demo.py`.
   ```python
   from ExampleAgency.agency import agency
   ```

   Make sure your agency.py has a global create_agency function that returns an Agency object.

4. **Test the agency:**
   - Simply run `python demo.py` from the `src/` directory.

