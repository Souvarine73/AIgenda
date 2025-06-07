"""
Docstring
"""

# import necessary modules
from .models import Tarea, get_session
from .schema import TaskCreate
from datetime import datetime
from loguru import logger
from typing import Optional
from datetime import date, timedelta
from sqlalchemy import func
from agents import function_tool

@function_tool
def create_task(title: str, description: str, due_date: datetime, database_url: Optional[str] = None) -> dict:
    """
    Create a new task in the database.
    
    Args:
    - title (str): The title of the task.
    - description (str): The description of the task.
    - due_date (datetime): The due date of the task.
    Returns:
    -dict: The created task as a dictionary.
    """

    # DEBUG: Ver exactamente qué recibimos
    logger.error(f"🔍 DEBUG - Received due_date: {due_date}")
    logger.error(f"🔍 DEBUG - Type: {type(due_date)}")
    logger.error(f"🔍 DEBUG - String representation: {str(due_date)}")

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

"""
TO DO: 
🥇 PRIORIDAD ALTA (Esenciales para chatbot básico)

get_all_tasks() - Listar todas las tareas ✅
get_task_by_id(id) - Obtener tarea específica ✅
delete_task(id) - Borrar tarea por ID ✅


🥈 PRIORIDAD MEDIA (Muy útiles para chatbot)

get_tasks_for_today() - Tareas de hoy ✅
get_upcoming_tasks(days=X) - Próximos X días (flexible)

🥉 PRIORIDAD BAJA (Nice to have)

get_tasks_by_date_range(start, end) - Rango personalizado
search_tasks(keyword) - Buscar por palabra clave
delete_all_tasks() - Borrar todas (útil para testing)
get_recent_tasks(days=7) - Tareas creadas recientemente
get_overdue_tasks() - Tareas vencidas (¡crítico para usuarios!) -> Depends on create update_task()
"""

@function_tool
def get_all_tasks(database_url: Optional[str] = None) -> list[dict]:
    """
    Retrieve a list of all tasks from the database.

    Args:
    - database_url (Optional[str]): The URL of the database. Defaults to None, which uses the default SQLite database.

    Returns:
    -list[dict]: A list of dictionaries representing all tasks in the database.

    Raises:
    - Exception: In case of error during retrieval.
    """
    try:
        logger.info("🔗 Connecting to the database")
        session = get_session(database_url or "sqlite:///data/tareas.db", debug=True)
        logger.success("✅ Database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Error connecting to the database: {e}")
        raise Exception(f"Error connecting to the database: {e}")
    
    try:
        logger.info("🔍 Retrieving all tasks from the database")
        tasks = session.query(Tarea).all()
        logger.success(f"✅ Retrieved {len(tasks)} tasks successfully")
        return [task.to_dict() for task in tasks]
    except Exception as e:
        logger.error(f"❌ Error retrieving tasks: {e}")
        raise Exception(f"Error retrieving tasks: {e}")
    finally:
        logger.info("🔒 Closing session")
        session.close()

@function_tool
def get_task_by_id(task_id: int, database_url: Optional[str] = None) -> dict:
    """
    Retrieve a task by its ID from the database.
    
    Args:
    - task_id (int): The id of the task to retrieve.
    - database_url (Optional[str]): The URL of the database. Defaults to None, which uses the default SQLite database.
    
    Returns: 
    - dict: The task as a dictionary.
    
    Raises:
    - Exception: In case of error during retrieval
    """
    if not isinstance(task_id, int) or task_id <= 0:
        logger.error(f"❌ Invalid task_id: {task_id}")
        raise ValueError(f"task_id must be a positive integer, got: {task_id}")

    try:
        logger.info("🔗 Connecting to the database")
        session = get_session(database_url or "sqlite:///data/tareas.db", debug=True)
        logger.success("✅ Database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Error connecting to the database: {e}")
        raise Exception(f"Error connecting to the database: {e}")
    
    try:
        logger.info(f"🔍 Retrieving task with ID {task_id} from the database")
        task = session.query(Tarea).filter_by(id=task_id).first()
        
        if not task:
            logger.warning(f"⚠️ Task with ID {task_id} not found")
            return {"error": f"Task with ID {task_id} not found"}
        
        logger.success(f"✅ Task with ID {task_id} retrieved successfully")
        return task.to_dict()
    except Exception as e:
        logger.error(f"❌ Error retrieving task with ID {task_id}: {e}")
        raise Exception(f"Error retrieving task with ID {task_id}: {e}")
    finally:
        logger.info("🔒 Closing session")
        session.close()
        
@function_tool
def delete_task(task_id: int, database_url: Optional[str] = None) -> dict:
    """
    Delete a task by its ID from the database.

    Args:
    - task_id (int): The id of the task to delete.
    - database_url (Optional[str]): The URL of the database. Defaults to None, which uses the default SQLite database.

    returns:
    - dict: A dictionary indicating the result of the deletion operation.
    """
    # check id
    if not isinstance(task_id, int) or task_id <= 0:
        logger.error(f"Invalid task_id: {task_id}")
        raise ValueError("❌ task_id must be a positive integer")
    
    try:
        logger.info("🔗 Connecting to the database")
        session = get_session(database_url or "sqlite:///data/tareas.db", debug=True)
        logger.success("✅ Database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Error connecting to the database: {e}")
        raise Exception(f"Error connecting to the database: {e}")
    
    try:
        logger.info(f"🔍 Deleting task with ID {task_id}")
        deleted_count = session.query(Tarea).filter_by(id=task_id).delete()
        if deleted_count == 0:
            logger.warning(f"⚠️ task with ID {task_id} not found")
            return {"error": f"task with ID {task_id} not found"}
        session.commit()
        logger.success(f"✅ Task with ID {task_id} deleted successfully")
        return {"message": f"Task with ID {task_id} deleted successfully"}
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Error deleting task with ID {task_id}: {e}")
        raise Exception(f"Error deleting task with ID {task_id}: {e}")
    finally:
        logger.info("🔒 Closing session")
        session.close()

@function_tool        
def get_tasks_for_today(database_url: Optional[str] = None) -> list[dict]:
    """
    Retrieve tasks that are due today from the databse.
    
    Args:
    - database_url (Optional[str]): The URL of the database. Defaults to None, which uses the default SQLite database.

    Returns:
    - list[dict]: A list of dictionaries representing tasks that are due today.
    """
    try:
        logger.info("🔗 Connecting to the database")
        session = get_session(database_url or "sqlite:///data/tareas.db", debug=True)
        logger.success("✅ Database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Error connecting to the database: {e}")
        raise Exception(f"Error connecting to the database: {e}")
    
    # Check if there is any task due today.
    try:
        today = date.today()
        logger.info(f"Retrieving tasks due today: {today}")
        tasks = session.query(Tarea).filter(func.date(Tarea.due_date) == today).all()
        tasks_list = [task.to_dict() for task in tasks]
        if not tasks_list:
            logger.warning("No tasks due today")
            return []
        logger.success(f"✅ Retrieved {len(tasks_list)} tasks due today")
        return tasks_list
    except Exception as e:
        logger.error(f"❌ Error retrieving tasks due today: {e}")
        raise Exception(f"❌ Error retrieving tasks due today: {e}")
    finally:
        logger.info("🔒 Closing session")
        session.close()
        
@function_tool
def get_upcoming_tasks(days: int, database_url: Optional[str] = None) -> list[dict]:
    """
    Retrieve tasks that are due within the next specified number of days from the database.

    Args:
    - days (int): The number of days to look ahead for upcoming tasks.
    - database_url (Optional[str]): The URL of the database. Defaults to None, which uses the default SQLite database.

    Returns:
    - list[dict]: A list of dictionaries representing tasks that are due within the next specified number of days.
    """
    if not isinstance(days, int) or days < 0:
        logger.error(f"❌ Invalid days parameter: {days}")
        raise ValueError("❌ Days must be a non negative integer")

    try:
        logger.info("🔗 Connecting to the database")
        session = get_session(database_url or "sqlite:///data/tareas.db", debug=True)
        logger.success("✅ Database connection established successfully")
    except Exception as e:
        logger.error(f"❌ Error connecting to the database: {e}")
        raise Exception(f"Error connecting to the database: {e}") 
    
    try:
        logger.info(f"Retrieving tasks due within the next {days} days")
        today = date.today()
        upcoming_date = today + timedelta(days=days)
        tasks = session.query(Tarea).filter(
            func.date(Tarea.due_date) >= today,
            func.date(Tarea.due_date) <= upcoming_date
        ).all()
        task_list = [task.to_dict() for task in tasks]

        if not task_list:
            logger.warning(f"No upcoming tasks found for the next {days} days")
            return []
        logger.success(f"Retrieved {len(task_list)} upcoming tasks successfully")
        return task_list
    except Exception as e:
        logger.error(f"❌ Error retrieving upcoming tasks: {e}")
        raise Exception(f"❌ Error retrieving upcoming tasks: {e}")
    finally:
        logger.info("🔒 Closing session")
        session.close()



        