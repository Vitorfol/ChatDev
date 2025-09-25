'''
Pydantic schemas for request and response validation.
This module defines the data models (schemas) used by the FastAPI application
for Students, Courses, and Teachers. It includes base schemas for creation/update
requests and read schemas used in responses. Email fields are validated using
pydantic's EmailStr and ORM mode is enabled where needed to allow returning
SQLAlchemy model instances directly.
'''
from typing import List, Optional
from pydantic import BaseModel, EmailStr
class CourseSimple(BaseModel):
    id: int
    title: str
    level: Optional[str]
    class Config:
        orm_mode = True
class TeacherSimple(BaseModel):
    id: int
    name: str
    email: Optional[EmailStr]
    class Config:
        orm_mode = True
# Student schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr
class StudentCreate(StudentBase):
    pass
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class StudentRead(StudentBase):
    id: int
    courses: List[CourseSimple] = []
    class Config:
        orm_mode = True
# Teacher schemas
class TeacherBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
class TeacherCreate(TeacherBase):
    pass
class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class TeacherRead(TeacherBase):
    id: int
    courses: List[CourseSimple] = []
    class Config:
        orm_mode = True
# Course schemas
class CourseBase(BaseModel):
    title: str
    description: Optional[str] = None
    level: Optional[str] = None
class CourseCreate(CourseBase):
    teacher_id: Optional[int] = None
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[str] = None
    teacher_id: Optional[int] = None
class CourseRead(CourseBase):
    id: int
    teacher: Optional[TeacherSimple] = None
    students: List[StudentRead] = []
    class Config:
        orm_mode = True
# Resolve any forward references (useful if circular references exist)
StudentRead.update_forward_refs()
TeacherRead.update_forward_refs()
CourseRead.update_forward_refs()