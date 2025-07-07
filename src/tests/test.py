from pathlib import Path
import sys

import pytest


def run_tests():
    """Run the complete test suite."""
    # Determine test paths
    project_root = Path(__file__).parent.parent
    test_paths = [
        str(project_root / "tests"),  # Core tests
        # str(project_root / "agents")  # Agent tests
    ]

    # Add pytest arguments
    pytest_args = [
        *test_paths,
        "-v",  # Verbose output
        "--tb=short",  # Shorter traceback format
        "--asyncio-mode=auto",  # Handle async tests
    ]

    # Run tests and return exit code
    return pytest.main(pytest_args)


if __name__ == "__main__":
    sys.exit(run_tests())
