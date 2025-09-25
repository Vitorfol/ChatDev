'''
Pydantic schemas for validation at the API boundary.
Schemas are tolerant to incremental migrations: optional fields won't break earlier versions.
'''
from typing import Optional
from pydantic import BaseModel
class StudentCreate(BaseModel):
    id: int
    email: Optional[str] = None
class StudentUpdate(BaseModel):
    email: Optional[str] = None
class StudentOut(BaseModel):
    id: int
    email: Optional[str] = None
class CourseCreate(BaseModel):
    id: int
    level: Optional[str] = None
class CourseUpdate(BaseModel):
    level: Optional[str] = None
class CourseOut(BaseModel):
    id: int
    level: Optional[str] = None
class TeacherCreate(BaseModel):
    id: int
class TeacherOut(BaseModel):
    id: int
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
class TeachingCreate(BaseModel):
    teacher_id: int
    course_id: int
class TeachingOut(BaseModel):
    id: int
    teacher_id: int
    course_id: int