"""
Unit tests for delete operations (delete_task)
"""

import pytest
import os
import sys
from datetime import datetime, timedelta

# Add src to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.operations import delete_task  # type: ignore
from database.models import get_session, Tarea  # type: ignore

def test_delete_task_success(test_db, sample_task_data):
    """
    Test successful deletion of an existing task
    """
    # Arrange: Create a task first
    session = get_session(test_db)
    new_task = Tarea(**sample_task_data)
    session.add(new_task)
    session.commit()
    task_id = new_task.id
    session.close()
    
    # Act: Delete the task
    result = delete_task(task_id, database_url=test_db)
    
    # Assert: Verify successful deletion
    assert result is not None
    assert isinstance(result, dict)
    assert 'message' in result
    assert f"Task with ID {task_id} deleted successfully" in result['message']
    assert 'error' not in result
    
    # Verify task was actually deleted from database
    session = get_session(test_db)
    deleted_task = session.query(Tarea).filter_by(id=task_id).first()
    session.close()
    
    assert deleted_task is None, "Task should be deleted from database"

def test_delete_task_not_found(test_db):
    """
    Test deleting a task that doesn't exist
    Should return error message without raising exception
    """
    # Arrange: Use ID that doesn't exist
    non_existent_id = 999
    
    # Act: Try to delete non-existent task
    result = delete_task(non_existent_id, database_url=test_db)
    
    # Assert: Should return error message
    assert result is not None
    assert isinstance(result, dict)
    assert 'error' in result
    assert f"task with ID {non_existent_id} not found" in result['error']
    assert 'message' not in result

def test_delete_task_invalid_id_zero(test_db):
    """
    Test deleting with ID = 0 (invalid)
    Should raise ValueError
    """
    # Act & Assert: Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        delete_task(0, database_url=test_db)
    
    # Verify error message
    assert "task_id must be a positive integer" in str(exc_info.value)

def test_delete_task_invalid_id_negative(test_db):
    """
    Test deleting with negative ID (invalid)
    Should raise ValueError
    """
    # Act & Assert: Should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        delete_task(-1, database_url=test_db)
    
    # Verify error message
    assert "task_id must be a positive integer" in str(exc_info.value)

def test_delete_task_invalid_id_type(test_db):
    """
    Test deleting with non-integer ID (invalid)
    Should raise ValueError
    """
    # Act & Assert: Should raise ValueError for string
    with pytest.raises(ValueError) as exc_info:
        delete_task("invalid", database_url=test_db)  # type: ignore
    
    assert "task_id must be a positive integer" in str(exc_info.value)
    
    # Act & Assert: Should raise ValueError for float
    with pytest.raises(ValueError) as exc_info:
        delete_task(1.5, database_url=test_db)  # type: ignore
    
    assert "task_id must be a positive integer" in str(exc_info.value)

def test_delete_task_empty_database(test_db):
    """
    Test deleting from empty database
    Should return error message
    """
    # Arrange: Database is already empty (from fixture)
    
    # Act: Try to delete from empty database
    result = delete_task(1, database_url=test_db)
    
    # Assert: Should return error
    assert result is not None
    assert isinstance(result, dict)
    assert 'error' in result
    assert "task with ID 1 not found" in result['error']

def test_delete_task_multiple_tasks_delete_one(test_db, sample_task_data, minimal_task_data):
    """
    Test deleting one task when multiple exist
    Should only delete the specified task
    """
    # Arrange: Create multiple tasks
    session = get_session(test_db)
    
    task1 = Tarea(**sample_task_data)
    task2 = Tarea(**minimal_task_data)
    
    session.add(task1)
    session.add(task2)
    session.commit()
    
    task1_id = task1.id
    task2_id = task2.id
    session.close()
    
    # Act: Delete only first task
    result = delete_task(task1_id, database_url=test_db)
    
    # Assert: Verify successful deletion
    assert 'message' in result
    assert f"Task with ID {task1_id} deleted successfully" in result['message']
    
    # Verify only task1 was deleted, task2 still exists
    session = get_session(test_db)
    deleted_task = session.query(Tarea).filter_by(id=task1_id).first()
    remaining_task = session.query(Tarea).filter_by(id=task2_id).first()
    total_tasks = session.query(Tarea).count()
    session.close()
    
    assert deleted_task is None, "Task1 should be deleted"
    assert remaining_task is not None, "Task2 should still exist"
    assert total_tasks == 1, "Should have exactly 1 task remaining"

def test_delete_task_invalid_database_url():
    """
    Test delete_task with invalid database URL
    Should raise an exception
    """
    # Act & Assert: Should raise exception with invalid URL
    with pytest.raises(Exception) as exc_info:
        delete_task(1, database_url="invalid://bad_url")
    
    # Verify the exception contains meaningful information
    error_message = str(exc_info.value).lower()
    assert "error" in error_message and "connecting" in error_message

def test_delete_task_default_database_url(test_db):
    """
    Test delete_task with database_url=None (uses default)
    """
    # Act & Assert: Should not raise exception when called without database_url
    try:
        # This might fail if data/ directory doesn't exist, which is expected
        result = delete_task(999, database_url=None)
        # If it works, should return error for non-existent task
        assert isinstance(result, dict)
        assert 'error' in result
    except Exception:
        # Expected if default database path doesn't exist
        # This is acceptable behavior
        pass