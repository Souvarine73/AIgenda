"""
Pydantic schemas for Task Manaement

Pydantic models for validating data that enters the database.
For data that exists we use the to_dict() method from the SQLAlchemy model.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class TaskCreate(BaseModel):
    """
    Schema for creating a nre task
    """
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: datetime

    @field_validator('title')
    @classmethod
    def validate_title(cls: object, v:str) -> str:
        """
        Clean whitespace and ensure title is not empty
        """
        if not v.strip():
            raise ValueError("Title cannot be empty")
        return v.strip()
    
    @field_validator('description')
    @classmethod
    def validate_description(cls: object, v:str) -> Optional[str]:
        """
        Clean whitespace in description
        """
        if v is not None:
            v = v.strip()
            return v if v else None
        return None
    
