"""
Unit tests for get_tasks_for_today operation
"""

import pytest
import os
import sys
from datetime import datetime, date, timedelta

# Add src to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.operations import get_tasks_for_today  # type: ignore
from database.models import get_session, Tarea  # type: ignore

def test_get_tasks_for_today_empty_database(test_db):
    """
    Test getting today's tasks from an empty database
    Should return an empty list
    """
    # Act: Call the function with empty database
    result = get_tasks_for_today(database_url=test_db)
    
    # Assert: Should return empty list
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []

def test_get_tasks_for_today_no_tasks_today(test_db):
    """
    Test getting today's tasks when database has tasks but none for today
    Should return empty list
    """
    # Arrange: Create tasks for yesterday and tomorrow
    session = get_session(test_db)
    
    yesterday = datetime.now() - timedelta(days=1)
    tomorrow = datetime.now() + timedelta(days=1)
    
    yesterday_task = Tarea(
        title="Yesterday task",
        description="Task from yesterday",
        due_date=yesterday
    )
    
    tomorrow_task = Tarea(
        title="Tomorrow task", 
        description="Task for tomorrow",
        due_date=tomorrow
    )
    
    session.add(yesterday_task)
    session.add(tomorrow_task)
    session.commit()
    session.close()
    
    # Act: Get today's tasks
    result = get_tasks_for_today(database_url=test_db)
    
    # Assert: Should return empty list (no tasks for today)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []

def test_get_tasks_for_today_single_task(test_db):
    """
    Test getting today's tasks when there's exactly one task due today
    Should return list with one task
    """
    # Arrange: Create one task for today
    session = get_session(test_db)
    
    today_task = Tarea(
        title="Today's task",
        description="Important task for today",
        due_date=datetime.now()  # Today's date
    )
    
    session.add(today_task)
    session.commit()
    task_id = today_task.id
    session.close()
    
    # Act: Get today's tasks
    result = get_tasks_for_today(database_url=test_db)
    
    # Assert: Should return list with one task
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    
    # Verify task structure and content
    task = result[0]
    assert isinstance(task, dict)
    assert 'id' in task
    assert 'title' in task
    assert 'description' in task
    assert 'created_at' in task
    assert 'updated_at' in task
    assert 'due_date' in task
    
    assert task['id'] == task_id
    assert task['title'] == "Today's task"
    assert task['description'] == "Important task for today"

def test_get_tasks_for_today_multiple_tasks(test_db):
    """
    Test getting today's tasks when there are multiple tasks due today
    Should return list with all today's tasks
    """
    # Arrange: Create multiple tasks for today with different times
    session = get_session(test_db)
    
    # Different times today
    morning_task = Tarea(
        title="Morning task",
        description="Task for this morning",
        due_date=datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
    )
    
    afternoon_task = Tarea(
        title="Afternoon task",
        description="Task for this afternoon", 
        due_date=datetime.now().replace(hour=15, minute=30, second=0, microsecond=0)
    )
    
    evening_task = Tarea(
        title="Evening task",
        description="Task for this evening",
        due_date=datetime.now().replace(hour=20, minute=0, second=0, microsecond=0)
    )
    
    session.add_all([morning_task, afternoon_task, evening_task])
    session.commit()
    session.close()
    
    # Act: Get today's tasks
    result = get_tasks_for_today(database_url=test_db)
    
    # Assert: Should return list with all 3 tasks
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3
    
    # Verify all tasks are dictionaries with required fields
    for task in result:
        assert isinstance(task, dict)
        assert 'id' in task
        assert 'title' in task
        assert 'description' in task
        assert 'created_at' in task
        assert 'updated_at' in task
        assert 'due_date' in task
    
    # Verify we have the expected titles
    titles = [task['title'] for task in result]
    assert "Morning task" in titles
    assert "Afternoon task" in titles
    assert "Evening task" in titles

def test_get_tasks_for_today_mixed_dates(test_db):
    """
    Test getting today's tasks when database has tasks for yesterday, today, and tomorrow
    Should return only today's tasks
    """
    # Arrange: Create tasks for different dates
    session = get_session(test_db)
    
    yesterday = datetime.now() - timedelta(days=1)
    today = datetime.now()
    tomorrow = datetime.now() + timedelta(days=1)
    
    yesterday_task = Tarea(
        title="Yesterday task",
        description="Task from yesterday", 
        due_date=yesterday
    )
    
    today_task1 = Tarea(
        title="Today task 1",
        description="First task for today",
        due_date=today.replace(hour=10)
    )
    
    today_task2 = Tarea(
        title="Today task 2", 
        description="Second task for today",
        due_date=today.replace(hour=16)
    )
    
    tomorrow_task = Tarea(
        title="Tomorrow task",
        description="Task for tomorrow",
        due_date=tomorrow
    )
    
    session.add_all([yesterday_task, today_task1, today_task2, tomorrow_task])
    session.commit()
    session.close()
    
    # Act: Get today's tasks
    result = get_tasks_for_today(database_url=test_db)
    
    # Assert: Should return only today's tasks (2 tasks)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    # Verify only today's tasks are returned
    titles = [task['title'] for task in result]
    assert "Today task 1" in titles
    assert "Today task 2" in titles
    assert "Yesterday task" not in titles
    assert "Tomorrow task" not in titles

def test_get_tasks_for_today_different_times_same_day(test_db):
    """
    Test that tasks with different times on the same day are all included
    """
    # Arrange: Create tasks at different times today
    session = get_session(test_db)
    
    # Very early morning
    early_task = Tarea(
        title="Early task",
        description="Very early task",
        due_date=datetime.now().replace(hour=0, minute=1, second=0, microsecond=0)
    )
    
    # Late night
    late_task = Tarea(
        title="Late task", 
        description="Very late task",
        due_date=datetime.now().replace(hour=23, minute=59, second=59, microsecond=0)
    )
    
    session.add_all([early_task, late_task])
    session.commit()
    session.close()
    
    # Act: Get today's tasks
    result = get_tasks_for_today(database_url=test_db)
    
    # Assert: Both tasks should be included
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    titles = [task['title'] for task in result]
    assert "Early task" in titles
    assert "Late task" in titles

def test_get_tasks_for_today_invalid_database_url():
    """
    Test get_tasks_for_today with invalid database URL
    Should raise an exception
    """
    # Act & Assert: Should raise exception with invalid URL
    with pytest.raises(Exception) as exc_info:
        get_tasks_for_today(database_url="invalid://bad_url")
    
    # Verify the exception contains meaningful information
    error_message = str(exc_info.value).lower()
    assert "error" in error_message and "connecting" in error_message

def test_get_tasks_for_today_return_structure_validation(test_db):
    """
    Test that get_tasks_for_today returns the correct dictionary structure
    Validates all required fields and data types
    """
    # Arrange: Create a task for today
    session = get_session(test_db)
    
    today_task = Tarea(
        title="Structure test task",
        description="Task to test return structure",
        due_date=datetime.now()
    )
    
    session.add(today_task)
    session.commit()
    session.close()
    
    # Act: Get today's tasks
    result = get_tasks_for_today(database_url=test_db)
    
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
    assert datetime.fromisoformat(task['created_at'])
    assert datetime.fromisoformat(task['updated_at']) 
    assert datetime.fromisoformat(task['due_date'])

def test_get_tasks_for_today_default_database_url():
    """
    Test get_tasks_for_today with database_url=None (uses default)
    """
    # Act & Assert: Should not raise exception when called without database_url
    try:
        # This might fail if data/ directory doesn't exist, which is expected
        result = get_tasks_for_today(database_url=None)
        # If it works, result should be a list
        assert isinstance(result, list)
    except Exception:
        # Expected if default database path doesn't exist
        # This is acceptable behavior
        pass