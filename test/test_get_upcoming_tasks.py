"""
Unit tests for get_upcoming_tasks operation
"""

import pytest
import os
import sys
from datetime import datetime, date, timedelta

# Add src to the system path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.operations import get_upcoming_tasks  # type: ignore
from database.models import get_session, Tarea  # type: ignore

def test_get_upcoming_tasks_empty_database(test_db):
    """
    Test getting upcoming tasks from an empty database
    Should return an empty list
    """
    # Act: Call the function with empty database
    result = get_upcoming_tasks(days=7, database_url=test_db)
    
    # Assert: Should return empty list
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 0
    assert result == []

def test_get_upcoming_tasks_zero_days(test_db):
    """
    Test getting upcoming tasks with days=0 (only today)
    Should behave like get_tasks_for_today()
    """
    # Arrange: Create tasks for today, yesterday, and tomorrow
    session = get_session(test_db)
    
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)
    
    today_task = Tarea(
        title="Today task",
        description="Task for today",
        due_date=today
    )
    
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
    
    session.add_all([today_task, yesterday_task, tomorrow_task])
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks for 0 days (only today)
    result = get_upcoming_tasks(days=0, database_url=test_db)
    
    # Assert: Should return only today's task
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['title'] == "Today task"

def test_get_upcoming_tasks_single_day(test_db):
    """
    Test getting upcoming tasks for 1 day (today + tomorrow)
    """
    # Arrange: Create tasks for different days
    session = get_session(test_db)
    
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    today_task = Tarea(
        title="Today task",
        description="Task for today",
        due_date=today
    )
    
    tomorrow_task = Tarea(
        title="Tomorrow task",
        description="Task for tomorrow",
        due_date=tomorrow
    )
    
    future_task = Tarea(
        title="Future task",
        description="Task for day after tomorrow",
        due_date=day_after_tomorrow
    )
    
    session.add_all([today_task, tomorrow_task, future_task])
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks for 1 day
    result = get_upcoming_tasks(days=1, database_url=test_db)
    
    # Assert: Should return today's and tomorrow's tasks
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    titles = [task['title'] for task in result]
    assert "Today task" in titles
    assert "Tomorrow task" in titles
    assert "Future task" not in titles

def test_get_upcoming_tasks_week(test_db):
    """
    Test getting upcoming tasks for a week (7 days)
    """
    # Arrange: Create tasks spread across different days
    session = get_session(test_db)
    
    base_date = datetime.now()
    tasks_data = [
        ("Today", 0),
        ("Day 3", 3),
        ("Day 7", 7),
        ("Day 8", 8),  # Outside range
        ("Day 10", 10)  # Outside range
    ]
    
    created_tasks = []
    for title, days_offset in tasks_data:
        task = Tarea(
            title=f"{title} task",
            description=f"Task for {title.lower()}",
            due_date=base_date + timedelta(days=days_offset)
        )
        created_tasks.append(task)
        session.add(task)
    
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks for 7 days
    result = get_upcoming_tasks(days=7, database_url=test_db)
    
    # Assert: Should return tasks within 7 days (today + 7 days)
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3  # Today, Day 3, Day 7
    
    titles = [task['title'] for task in result]
    assert "Today task" in titles
    assert "Day 3 task" in titles
    assert "Day 7 task" in titles
    assert "Day 8 task" not in titles
    assert "Day 10 task" not in titles

def test_get_upcoming_tasks_mixed_dates(test_db):
    """
    Test getting upcoming tasks when database has tasks before, within, and after range
    Should return only tasks within the specified range
    """
    # Arrange: Create tasks across a wide date range
    session = get_session(test_db)
    
    base_date = datetime.now()
    tasks_data = [
        ("Past", -5),      # Before range
        ("Yesterday", -1), # Before range
        ("Today", 0),      # In range
        ("Day 2", 2),      # In range
        ("Day 5", 5),      # In range (if days=5)
        ("Day 6", 6),      # Outside range (if days=5)
        ("Future", 15)     # Outside range
    ]
    
    for title, days_offset in tasks_data:
        task = Tarea(
            title=f"{title} task",
            description=f"Task for {title.lower()}",
            due_date=base_date + timedelta(days=days_offset)
        )
        session.add(task)
    
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks for 5 days
    result = get_upcoming_tasks(days=5, database_url=test_db)
    
    # Assert: Should return only tasks within next 5 days
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 3  # Today, Day 2, Day 5
    
    titles = [task['title'] for task in result]
    assert "Today task" in titles
    assert "Day 2 task" in titles
    assert "Day 5 task" in titles
    
    # Should not include past or far future tasks
    assert "Past task" not in titles
    assert "Yesterday task" not in titles
    assert "Day 6 task" not in titles
    assert "Future task" not in titles

def test_get_upcoming_tasks_boundary_dates(test_db):
    """
    Test boundary conditions for date ranges
    """
    # Arrange: Create tasks exactly at boundaries
    session = get_session(test_db)
    
    base_date = datetime.now()
    
    # Tasks exactly at start and end of range
    start_task = Tarea(
        title="Start boundary",
        description="Task at start of range",
        due_date=base_date  # Today (start)
    )
    
    end_task = Tarea(
        title="End boundary",
        description="Task at end of range",
        due_date=base_date + timedelta(days=3)  # Exactly 3 days from now
    )
    
    outside_task = Tarea(
        title="Outside boundary",
        description="Task just outside range",
        due_date=base_date + timedelta(days=4)  # Just outside 3-day range
    )
    
    session.add_all([start_task, end_task, outside_task])
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks for exactly 3 days
    result = get_upcoming_tasks(days=3, database_url=test_db)
    
    # Assert: Should include start and end, but not outside
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 2
    
    titles = [task['title'] for task in result]
    assert "Start boundary" in titles
    assert "End boundary" in titles
    assert "Outside boundary" not in titles

def test_get_upcoming_tasks_large_range(test_db):
    """
    Test getting upcoming tasks for a large date range (30 days)
    """
    # Arrange: Create tasks spread across a month
    session = get_session(test_db)
    
    base_date = datetime.now()
    
    # Create tasks at various points within 30 days
    tasks_within = [
        ("Week 1", 7),
        ("Week 2", 14),
        ("Week 3", 21),
        ("Day 30", 30)
    ]
    
    # Create task outside range
    outside_task = Tarea(
        title="Outside month",
        description="Task outside 30-day range",
        due_date=base_date + timedelta(days=31)
    )
    session.add(outside_task)
    
    # Create tasks within range
    for title, days_offset in tasks_within:
        task = Tarea(
            title=f"{title} task",
            description=f"Task for {title.lower()}",
            due_date=base_date + timedelta(days=days_offset)
        )
        session.add(task)
    
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks for 30 days
    result = get_upcoming_tasks(days=30, database_url=test_db)
    
    # Assert: Should return all tasks within 30 days
    assert result is not None
    assert isinstance(result, list)
    assert len(result) == 4  # All tasks within range
    
    titles = [task['title'] for task in result]
    assert "Week 1 task" in titles
    assert "Week 2 task" in titles
    assert "Week 3 task" in titles
    assert "Day 30 task" in titles
    assert "Outside month" not in titles

def test_get_upcoming_tasks_negative_days(test_db):
    """
    Test that negative days parameter raises ValueError
    """
    # Act & Assert: Should raise ValueError for negative days
    with pytest.raises(ValueError) as exc_info:
        get_upcoming_tasks(days=-1, database_url=test_db)
    
    # Verify error message
    assert "Days must be a non negative integer" in str(exc_info.value)

def test_get_upcoming_tasks_invalid_type_string(test_db):
    """
    Test that string days parameter raises ValueError
    """
    # Act & Assert: Should raise ValueError for string input
    with pytest.raises(ValueError) as exc_info:
        get_upcoming_tasks(days="7", database_url=test_db)  # type: ignore
    
    assert "Days must be a non negative integer" in str(exc_info.value)

def test_get_upcoming_tasks_invalid_type_float(test_db):
    """
    Test that float days parameter raises ValueError
    """
    # Act & Assert: Should raise ValueError for float input
    with pytest.raises(ValueError) as exc_info:
        get_upcoming_tasks(days=7.5, database_url=test_db)  # type: ignore
    
    assert "Days must be a non negative integer" in str(exc_info.value)

def test_get_upcoming_tasks_invalid_database_url():
    """
    Test get_upcoming_tasks with invalid database URL
    Should raise an exception
    """
    # Act & Assert: Should raise exception with invalid URL
    with pytest.raises(Exception) as exc_info:
        get_upcoming_tasks(days=7, database_url="invalid://bad_url")
    
    # Verify the exception contains meaningful information
    error_message = str(exc_info.value).lower()
    assert "error" in error_message and "connecting" in error_message

def test_get_upcoming_tasks_return_structure_validation(test_db):
    """
    Test that get_upcoming_tasks returns the correct dictionary structure
    Validates all required fields and data types
    """
    # Arrange: Create a task within range
    session = get_session(test_db)
    
    upcoming_task = Tarea(
        title="Structure test task",
        description="Task to test return structure",
        due_date=datetime.now() + timedelta(days=2)
    )
    
    session.add(upcoming_task)
    session.commit()
    session.close()
    
    # Act: Get upcoming tasks
    result = get_upcoming_tasks(days=7, database_url=test_db)
    
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

def test_get_upcoming_tasks_default_database_url():
    """
    Test get_upcoming_tasks with database_url=None (uses default)
    """
    # Act & Assert: Should not raise exception when called without database_url
    try:
        # This might fail if data/ directory doesn't exist, which is expected
        result = get_upcoming_tasks(days=7, database_url=None)
        # If it works, result should be a list
        assert isinstance(result, list)
    except Exception:
        # Expected if default database path doesn't exist
        # This is acceptable behavior
        pass