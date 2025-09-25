'''
Pydantic models (schemas) for request and response bodies.
Defines Base, Create, Update and Read schemas for Student, Course, Teacher, Enrollment, and CourseTeacher.
'''
from pydantic import BaseModel
from typing import Optional
# Student
class StudentBase(BaseModel):
    name: str
    # Use plain Optional[str] for email to avoid requiring the external "email_validator" package
    # (EmailStr from pydantic triggers an import of email_validator). This keeps the test/runtime
    # environment lightweight while still allowing an email field.
    email: Optional[str] = None
class StudentCreate(StudentBase):
    pass
class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
class StudentRead(StudentBase):
    id: int
    class Config:
        orm_mode = True
# Course
class CourseBase(BaseModel):
    title: str
    level: Optional[str] = None
class CourseCreate(CourseBase):
    pass
class CourseUpdate(BaseModel):
    title: Optional[str] = None
    level: Optional[str] = None
class CourseRead(CourseBase):
    id: int
    class Config:
        orm_mode = True
# Teacher
class TeacherBase(BaseModel):
    name: str
    department: Optional[str] = None
class TeacherCreate(TeacherBase):
    pass
class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
class TeacherRead(TeacherBase):
    id: int
    class Config:
        orm_mode = True
# Enrollment
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
class EnrollmentRead(BaseModel):
    id: int
    student_id: int
    course_id: int
    class Config:
        orm_mode = True
# CourseTeacher (assignment)
class CourseTeacherCreate(BaseModel):
    course_id: int
    teacher_id: int
class CourseTeacherRead(BaseModel):
    id: int
    course_id: int
    teacher_id: int
    class Config:
        orm_mode = True