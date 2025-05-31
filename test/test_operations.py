"""
Unit test for database operations
"""

import pytest
import os
import sys
from datetime import datetime

# Add src to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.operations import create_task # type: ignore
from database.models import get_session, Tarea # type: ignore

def test_create_task_success(test_db, sample_task_data):
    """
    Test successful creation of a task with all fields
    """
    # Arrange: sample_task_data comes from fixture
    
    # Act: Execute the function
    result = create_task(**sample_task_data, database_url=test_db)

        # Assert: Verify the result structure
    assert result is not None
    assert isinstance(result, dict)
    
    # Verify required fields are present
    assert 'id' in result
    assert 'title' in result
    assert 'description' in result
    assert 'created_at' in result
    assert 'updated_at' in result
    assert 'due_date' in result
    
    # Verify field values match input
    assert result['title'] == sample_task_data['title']
    assert result['description'] == sample_task_data['description']
    assert result['id'] is not None  # Should be auto-generated
    
    # Verify the task was actually saved to database
    session = get_session(test_db)
    saved_task = session.query(Tarea).filter_by(id=result['id']).first()
    session.close()
    
    assert saved_task is not None
    assert saved_task.title == sample_task_data['title']
    assert saved_task.description == sample_task_data['description']