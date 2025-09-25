'''
Pydantic models (schemas) for request and response validation in API endpoints.
'''
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
# Student schemas
class StudentBase(BaseModel):
    name: str = Field(..., example="Alice Smith")
    email: EmailStr = Field(..., example="alice@example.com")
class StudentCreate(StudentBase):
    pass
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
class StudentOut(StudentBase):
    id: int
    class Config:
        orm_mode = True
# Course schemas
class CourseBase(BaseModel):
    title: str = Field(..., example="Introduction to Programming")
    level: str = Field(..., example="Undergraduate")
class CourseCreate(CourseBase):
    pass
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
class CourseOut(CourseBase):
    id: int
    class Config:
        orm_mode = True
# Teacher schemas
class TeacherBase(BaseModel):
    name: str = Field(..., example="Dr. John Doe")
    department: str = Field(..., example="Computer Science")
class TeacherCreate(TeacherBase):
    pass
class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
class TeacherOut(TeacherBase):
    id: int
    class Config:
        orm_mode = True
# Relationship schemas
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
class TeachingCreate(BaseModel):
    teacher_id: int
    course_id: int
class EnrollmentOut(BaseModel):
    student_id: int
    course_id: int
    class Config:
        orm_mode = True
class TeachingOut(BaseModel):
    teacher_id: int
    course_id: int
    class Config:
        orm_mode = True