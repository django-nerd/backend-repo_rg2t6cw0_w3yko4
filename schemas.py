"""
Database Schemas for the Timetable & Resources App

Each Pydantic model corresponds to a MongoDB collection. The collection
name is the lowercase of the class name.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal

class Timetable(BaseModel):
    """
    Timetable collection schema
    Collection name: "timetable"
    """
    day: Literal["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"] = Field(..., description="Day of the week")
    subject: str = Field(..., description="Subject or activity name")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    location: Optional[str] = Field(None, description="Room or location")
    notes: Optional[str] = Field(None, description="Additional notes")

class Resource(BaseModel):
    """
    Resource collection schema
    Collection name: "resource"
    """
    title: str = Field(..., description="Resource title")
    url: Optional[str] = Field(None, description="Link to resource")
    topic: Optional[str] = Field(None, description="Topic or tag")
    description: Optional[str] = Field(None, description="Short description")

class Doubt(BaseModel):
    """
    Doubt (Q&A) collection schema
    Collection name: "doubt"
    """
    question: str = Field(..., description="Student question")
    student_name: Optional[str] = Field(None, description="Name of the student")
    answer: Optional[str] = Field(None, description="Answer to the question")
    answered_by: Optional[str] = Field(None, description="Name of the person who answered")
    status: Literal["open", "answered"] = Field("open", description="Current status of the doubt")
