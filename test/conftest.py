"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

# add src to the system path
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.models import create_database, get_session, Base # type: ignore


@pytest.fixture(scope='function')
def test_db():
    """
    Create a temporary SQLite database for testing.

    Yields:
    - A Database URL for the temporary database.    
    """
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()

    db_url = f"sqlite:///{temp_db.name}"

    # Create all tables in the temporary databse
    create_database(db_url, debug=True)

    yield db_url

    # Clean up the temporary database 
    try:
        import time
        time.sleep(0.1)  
        os.unlink(temp_db.name)
    except PermissionError:
        pass  

@pytest.fixture()
def sample_task_data():
    """
    Provides sample task data for testing
    
    Returns:
        dict: Dictionary with valid task data
    """
    return {
        "title": "Test Task",
        "description": "Test description for the task", 
        "due_date": datetime.now() + timedelta(days=1)
    }

@pytest.fixture
def minimal_task_data():
    """
    Provides minimal task data (without description)
    
    Returns:
        dict: Dictionary with minimal valid task data
    """
    return {
        "title": "Minimal Test Task",
        "description": None,
        "due_date": datetime.now() + timedelta(days=2)
    }

@pytest.fixture
def invalid_task_data():
    """
    Provides various invalid task data for error testing
    
    Returns:
        dict: Dictionary with different invalid data sets
    """
    return {
        "empty_title": {
            "title": "",
            "description": "Valid description",
            "due_date": datetime.now() + timedelta(days=1)
        },
        "long_title": {
            "title": "x" * 201,  # Too long (max 200)
            "description": "Valid description",
            "due_date": datetime.now() + timedelta(days=1)
        },
        "spaces_only_title": {
            "title": "   ",  # Only spaces
            "description": "Valid description", 
            "due_date": datetime.now() + timedelta(days=1)
        }
    }