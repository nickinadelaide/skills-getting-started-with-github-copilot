import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, INITIAL_ACTIVITIES


@pytest.fixture
def client():
    """Provide a TestClient for making requests to the app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test.
    
    This fixture automatically runs before each test to ensure test isolation.
    """
    # Import here to get the module-level activities reference
    from app import activities as app_activities
    
    # Clear and reset to initial state
    app_activities.clear()
    app_activities.update(deepcopy(INITIAL_ACTIVITIES))
    
    yield
    
    # Cleanup after test (optional, but good practice)
    app_activities.clear()
    app_activities.update(deepcopy(INITIAL_ACTIVITIES))
