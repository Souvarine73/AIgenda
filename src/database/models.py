"""
Task Management Module - Database Models

This module provides the data model definition for a task management system
using SQLAlchemy as the ORM. It includes the task table definition and
utility functions for database connection and configuration.

Main Components:
   - Tarea: SQLAlchemy model representing a task in the database
   - create_database(): Function to create the database and tables
   - get_session(): Function to obtain a database session

Usage Example:
   from task_models import Tarea, get_session
   
   # Create a new task
   session = get_session()
   new_task = Tarea(
       title="Complete project",
       description="Finish the development of the task module",
       due_date=datetime(2025, 6, 15)
   )
   session.add(new_task)
   session.commit()

Default Database:
   SQLite stored at: data/tareas.db

Dependencies:
   - SQLAlchemy: ORM for database management
   - datetime: Date and timestamp handling
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Base class for SQLAlchemy models
Base = declarative_base()

class Tarea(Base):
    """
    Modelo para la tabla de tareas
    
    Campos:
    - id: Identificador único (auto-incrementa)
    - titulo: Título de la tarea (obligatorio, máx 200 chars)
    - descripcion: Descripción detallada (opcional)
    - fecha_creacion: Cuando se creó (automático)
    - fecha_actualizacion: Última modificación (automático)
    - fecha_vencimiento: Cuándo vence la tarea (opcional)
    """

    __tablename__ = 'tareas'

    # fields
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
        )   
    due_date = Column(DateTime, nullable=False)

    # Methods
    def __repr__(self):
        """
        Legible string representation of the database model
        """
        return f"<Tarea(id={self.id}, title='{self.title}', due_date='{self.due_date}')>"
    
    def to_dict(self):
        """
        Convert the model instance to a dictionary
        """
        model_instance = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None, # type: ignore
            'updated_at': self.updated_at.isoformat() if self.updated_at else None, # type: ignore
            'due_date': self.due_date.isoformat() if self.due_date else None # type: ignore
        }

        return model_instance
    
def create_database(database_url="sqlite:///data/tareas.db", debug=False):
    """
    Create the dabase and tables if the don't exist
    
    Args:
    - databse_url: URL for the databse connection (default: SQLite in data/tareas.db)
    - debug: If True, print SQL statements (default: False)
    """

    engine = create_engine(database_url, echo=debug)
    Base.metadata.create_all(engine)
    return engine

def get_session(database_url="sqlite:///data/tareas.db", debug=False):
    """
    Get a new session for the databse

    Args:
    -database_url: URL for the database coneection (default: SQLite in data/tareas.db)
    - debug: If Truem, print SQL statements (default: false)

    Retunrs:
    - Sesscion: A new SQLAlchemy session for interacting with the database
    """
    engine = create_database(database_url, debug)
    Session = sessionmaker(bind=engine)
    return Session()

