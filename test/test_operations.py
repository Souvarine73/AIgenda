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

def test_create_task_minimal(test_db, minimal_task_data):
    """
    Test creation of a task without description (minimal required fields)
    """
    # Arrange: minimal_task_data comes from fixture
    
    # Act: Execute the function with temporary database
    result = create_task(**minimal_task_data, database_url=test_db)
    
    # Assert: Verify the result
    assert result is not None
    assert isinstance(result, dict)
    
    # Verify required fields
    assert 'id' in result
    assert 'title' in result
    assert result['title'] == minimal_task_data['title']
    
    # Verify description is None (not provided)
    assert result['description'] is None
    
    # Verify task exists in database
    session = get_session(test_db)
    saved_task = session.query(Tarea).filter_by(id=result['id']).first()
    session.close()
    
    assert saved_task is not None
    assert saved_task.title == minimal_task_data['title']
    assert saved_task.description is None

def test_create_task_returns_correct_structure(test_db, sample_task_data):
    """
    Test that create_task returns the expected dictionary structure
    """
    # Act: Execute with temporary database
    result = create_task(**sample_task_data, database_url=test_db)
    
    # Assert: Check structure and data types
    expected_keys = {'id', 'title', 'description', 'created_at', 'updated_at', 'due_date'}
    actual_keys = set(result.keys())
    
    assert actual_keys == expected_keys, f"Missing or extra keys. Expected: {expected_keys}, Got: {actual_keys}"
    
    # Verify data types
    assert isinstance(result['id'], int)
    assert isinstance(result['title'], str)
    assert isinstance(result['created_at'], str)  # ISO format string
    assert isinstance(result['updated_at'], str)  # ISO format string
    assert isinstance(result['due_date'], str)    # ISO format string
    
    # description can be str or None
    assert result['description'] is None or isinstance(result['description'], str)

def test_create_task_empty_title(test_db, invalid_task_data):
    """
    Test that creating a task with empty title raises ValidationError
    """
    # Arrange: Get invalid data with empty title
    empty_title_data = invalid_task_data["empty_title"]
    
    # Act & Assert: Should raise an exception
    with pytest.raises(Exception) as exc_info:
        create_task(**empty_title_data, database_url=test_db)
    
    # Verify it's a validation error (from Pydantic)
    assert "Title cannot be empty" in str(exc_info.value) or "validation" in str(exc_info.value).lower()
    
    # Verify no task was created in database
    session = get_session(test_db)
    task_count = session.query(Tarea).count()
    session.close()
    
    assert task_count == 0, "No task should be created when validation fails"

def test_create_task_title_too_long(test_db, invalid_task_data):
    """
    Test that creating a task with title exceeding 200 characters raises ValidationError
    """
    # Arrange: Get invalid data with long title
    long_title_data = invalid_task_data["long_title"]
    
    # Act & Assert: Should raise an exception
    with pytest.raises(Exception) as exc_info:
        create_task(**long_title_data, database_url=test_db)
    
    # Verify it's a validation error about title length
    error_message = str(exc_info.value).lower()
    assert "validation" in error_message or "length" in error_message or "200" in error_message
    
    # Verify no task was created in database
    session = get_session(test_db)
    task_count = session.query(Tarea).count()
    session.close()
    
    assert task_count == 0, "No task should be created when title validation fails"

def test_create_task_spaces_only_title(test_db, invalid_task_data):
    """
    Test that creating a task with title containing only spaces raises ValidationError
    """
    # Arrange: Get invalid data with spaces-only title
    spaces_title_data = invalid_task_data["spaces_only_title"]
    
    # Act & Assert: Should raise an exception
    with pytest.raises(Exception) as exc_info:
        create_task(**spaces_title_data, database_url=test_db)
    
    # Verify it's a validation error about empty title
    # (spaces get stripped by Pydantic validator, so it becomes empty)
    error_message = str(exc_info.value).lower()
    assert "title cannot be empty" in error_message or "validation" in error_message
    
    # Verify no task was created in database
    session = get_session(test_db)
    task_count = session.query(Tarea).count()
    session.close()
    
    assert task_count == 0, "No task should be created when title is only spaces"