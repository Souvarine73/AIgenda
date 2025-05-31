"""
Docstring
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 
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

