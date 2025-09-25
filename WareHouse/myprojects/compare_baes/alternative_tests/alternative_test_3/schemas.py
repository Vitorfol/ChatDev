'''
Pydantic schemas for request/response validation: Student, Teacher, Course.
This module defines:
- Level enum for course levels.
- Pydantic models for Student, Teacher, and Course used for
  request validation and response serialization.
These schemas are designed to work with the SQLAlchemy models and
crud utilities in the application. The ORM-compatible response
models include orm_mode = True so FastAPI can return SQLAlchemy
objects directly.
'''
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, EmailStr, Field
class Level(str, Enum):
    """
    Allowed levels for a Course. Using str + Enum so Pydantic treats values as strings
    (compatible with SQLAlchemy string column).
    """
    beginner = "beginner"
    intermediate = "intermediate"
    advanced = "advanced"
# --------------------
# Student Schemas
# --------------------
class StudentBase(BaseModel):
    """
    Shared properties for Student.
    """
    name: str
    email: EmailStr
class StudentCreate(StudentBase):
    """
    Properties required to create a student.
    """
    pass
class StudentUpdate(BaseModel):
    """
    Properties allowed to update for a student. All optional.
    """
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class StudentRead(StudentBase):
    """
    Properties returned for a student.
    """
    id: int
    class Config:
        orm_mode = True
# --------------------
# Teacher Schemas
# --------------------
class TeacherBase(BaseModel):
    """
    Shared properties for Teacher.
    """
    name: str
class TeacherCreate(TeacherBase):
    """
    Properties required to create a teacher.
    """
    pass
class TeacherUpdate(BaseModel):
    """
    Properties allowed to update for a teacher.
    """
    name: Optional[str] = None
class TeacherRead(TeacherBase):
    """
    Properties returned for a teacher.
    """
    id: int
    class Config:
        orm_mode = True
# --------------------
# Course Schemas
# --------------------
class CourseBase(BaseModel):
    """
    Shared properties for Course.
    Use Level enum to validate allowed values.
    """
    title: str
    level: Level  # e.g., 'beginner', 'intermediate', 'advanced'
class CourseCreate(CourseBase):
    """
    Properties required to create a course. Teacher assignment is optional.
    """
    teacher_id: Optional[int] = None
class CourseUpdate(BaseModel):
    """
    Properties allowed to update for a course.
    """
    title: Optional[str] = None
    level: Optional[Level] = None
    teacher_id: Optional[int] = None
class CourseRead(CourseBase):
    """
    Properties returned for a course, including id and optional teacher.
    Includes the list of students (default empty list).
    """
    id: int
    teacher: Optional[TeacherRead] = None
    students: List[StudentRead] = Field(default_factory=list)
    class Config:
        orm_mode = True