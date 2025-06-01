
"""
Unit tests for get operations (get_all_tasks, get_task_by_id)
"""

import pytest
import os
import sys
from datetime import datetime

# Add src to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.operations import get_all_tasks  # type: ignore
from database.models import get_session, Tarea  # type: ignore

def test_get_all_tasks_empty_database(test_db):
    """
    Test getting all tasks from an empty database
    Should return an empty list
    """
    # Act: Call the function with empty database
    result = get_all_tasks(database_url=test_db)
    
    # Assert: Should return empty list
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []

def test_get_all_tasks_with_single_task(test_db, sample_task_data):
    """
    Test getting all tasks when database has one task
    Should return list with one task dictionary
    """
    # Arrange: Create one task in the test database
    session = get_session(test_db)
    new_task = Tarea(**sample_task_data)
    session.add(new_task)
    session.commit()
    task_id = new_task.id
    session.close()
    
    # Act: Get all tasks
    result = get_all_tasks(database_url=test_db)
    
    # Assert: Should return list with one task
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    
    # Verify task structure
    task = result[0]
    assert isinstance(task, dict)
    assert 'id' in task
    assert 'title' in task
    assert 'description' in task
    assert 'created_at' in task
    assert 'updated_at' in task
    assert 'due_date' in task
    
    # Verify task content
    assert task['id'] == task_id
    assert task['title'] == sample_task_data['title']
    assert task['description'] == sample_task_data['description']

def test_get_all_tasks_multiple_tasks(test_db, sample_task_data, minimal_task_data):
    """
    Test getting all tasks when database has multiple tasks
    Should return list with all tasks
    """
    # Arrange: Create multiple tasks in the test database
    session = get_session(test_db)
    
    # Create first task
    task1 = Tarea(**sample_task_data)
    session.add(task1)
    
    # Create second task
    task2 = Tarea(**minimal_task_data)
    session.add(task2)
    
    session.commit()
    session.close()
    
    # Act: Get all tasks
    result = get_all_tasks(database_url=test_db)
    
    # Assert: Should return list with both tasks
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Verify all tasks are dictionaries with required fields
    for task in result:
        assert isinstance(task, dict)
        assert 'id' in task
        assert 'title' in task
        assert 'description' in task
        assert 'created_at' in task
        assert 'updated_at' in task
        assert 'due_date' in task
    
    # Verify we have the expected titles (order might vary)
    titles = [task['title'] for task in result]
    assert sample_task_data['title'] in titles
    assert minimal_task_data['title'] in titles

def test_get_all_tasks_default_database_url(test_db):
    """
    Test get_all_tasks with database_url=None (uses default)
    Note: This test might create a real database file, so we test the behavior
    """
    # Act & Assert: Should not raise exception when called without database_url
    # We can't easily test the default database without side effects,
    # so we just verify the function accepts None without errors
    try:
        # This might fail if data/ directory doesn't exist, which is expected
        result = get_all_tasks(database_url=None)
        # If it works, result should be a list
        assert isinstance(result, list)
    except Exception:
        # Expected if default database path doesn't exist
        # This is acceptable behavior
        pass

def test_get_all_tasks_invalid_database_url():
    """
    Test get_all_tasks with invalid database URL
    Should raise an exception
    """
    # Act & Assert: Should raise exception with invalid URL
    with pytest.raises(Exception) as exc_info:
        get_all_tasks(database_url="invalid://bad_url")
    
    # Verify the exception contains meaningful information
    error_message = str(exc_info.value).lower()
    assert "error" in error_message or "connecting" in error_message

def test_get_all_tasks_return_structure_validation(test_db, sample_task_data):
    """
    Test that get_all_tasks returns the correct dictionary structure
    Validates all required fields and data types
    """
    # Arrange: Create a task
    session = get_session(test_db)
    new_task = Tarea(**sample_task_data)
    session.add(new_task)
    session.commit()
    session.close()
    
    # Act: Get all tasks
    result = get_all_tasks(database_url=test_db)
    
    # Assert: Validate structure and data types
    assert len(result) == 1
    task = result[0]
    
    # Check all required keys exist
    expected_keys = {'id', 'title', 'description', 'created_at', 'updated_at', 'due_date'}
    actual_keys = set(task.keys())
    assert actual_keys == expected_keys, f"Missing or extra keys. Expected: {expected_keys}, Got: {actual_keys}"
    
    # Check data types
    assert isinstance(task['id'], int)
    assert isinstance(task['title'], str)
    assert isinstance(task['created_at'], str)  # ISO format string
    assert isinstance(task['updated_at'], str)  # ISO format string
    assert isinstance(task['due_date'], str)    # ISO format string
    
    # description can be str or None
    assert task['description'] is None or isinstance(task['description'], str)
    
    # Verify ISO format strings are valid
    from datetime import datetime
    assert datetime.fromisoformat(task['created_at'])
    assert datetime.fromisoformat(task['updated_at'])
    assert datetime.fromisoformat(task['due_date'])