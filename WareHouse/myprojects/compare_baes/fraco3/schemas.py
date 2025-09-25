'''
Pydantic schemas for request/response validation and serialization for Students, Courses, and Teachers.
This module defines the Base, Create, Update and Read schemas used by the FastAPI routers.
'''
from typing import List, Optional, TYPE_CHECKING
from pydantic import BaseModel, EmailStr, Field
# Teacher schemas
class TeacherBase(BaseModel):
    name: str
class TeacherCreate(TeacherBase):
    pass
class TeacherUpdate(BaseModel):
    name: Optional[str] = None
class TeacherInCourse(BaseModel):
    id: int
    name: str
    class Config:
        orm_mode = True
class TeacherRead(TeacherBase):
    id: int
    class Config:
        orm_mode = True
# Course schemas
class CourseBase(BaseModel):
    title: str
    level: int  # level attribute required
class CourseCreate(CourseBase):
    teacher_id: Optional[int] = None
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[int] = None
    teacher_id: Optional[int] = None
class CourseInStudent(BaseModel):
    id: int
    title: str
    level: int
    class Config:
        orm_mode = True
class CourseRead(CourseBase):
    id: int
    teacher: Optional[TeacherInCourse] = None
    students: List["StudentInCourse"] = Field(default_factory=list)
    class Config:
        orm_mode = True
# Student schemas
class StudentBase(BaseModel):
    name: str
    email: EmailStr  # email field added
class StudentCreate(StudentBase):
    pass
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class StudentInCourse(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config:
        orm_mode = True
class StudentRead(StudentBase):
    id: int
    courses: List[CourseInStudent] = Field(default_factory=list)
    class Config:
        orm_mode = True
# Resolve forward references for Pydantic models that reference each other
CourseRead.update_forward_refs()
StudentRead.update_forward_refs()