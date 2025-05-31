"""
Docstring
"""

# import necessary modules
from .models import Tarea, get_session
from .schema import TaskCreate
from datetime import datetime
from loguru import logger


def create_task(title: str, description: str, due_date: datetime, database_url = None) -> dict:
    """
    Create a new task in the database.
    
    Args:
    - title (str): The title of the task.
    - description (str): The description of the task.
    - due_date (datetime): The due date of the task.
    Returns:
    -dict: The created task as a dictionary.
    """

    # validate input data
    logger.info("1️⃣ Validating input data for task creation")
    task_data = TaskCreate(title=title, description=description, due_date=due_date)
    logger.success("✅ Input data validated successfully")
    logger.debug(f"Task data: {task_data}")

    # create a new task instance
    task_data_dict = task_data.model_dump()
    
    logger.info("2️⃣ Creating new task instance")
    new_task = Tarea(**task_data_dict)
    logger.success("✅ New task instance created successfully")
    logger.debug(f"New task: {new_task}")

    # get a new session
    session = get_session(database_url or "sqlite:///data/tareas.db", debug=True)
    
    # add the new task to the session
    try:
        logger.info("3️⃣ Adding new task to the session")
        session.add(new_task)
        session.commit()
        logger.success("✅ Task added to the session and committed successfully")
        return new_task.to_dict()
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error creating task: {e}")
        raise Exception(f"Error creating task: {e}")
    finally:
        logger.info("4️⃣ Closing session")
        session.close()

        