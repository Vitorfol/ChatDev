'''
Domain entities (Pydantic and lightweight dataclasses) for Students, Courses, Enrollments, Teachers.
These classes represent the core vocabulary (identifiers/documentation) of the domain and are preserved
across migrations so that higher-level services and APIs keep semantic stability.
'''
from typing import Optional
from pydantic import BaseModel
class StudentIn(BaseModel):
    """
    Data required to create or update a Student.
    'email' may be absent for older schema versions; keep it optional to preserve compatibility.
    """
    id: Optional[int] = None
    email: Optional[str] = None
class StudentOut(BaseModel):
    """
    Student representation returned to clients.
    """
    id: int
    email: Optional[str] = None
class CourseIn(BaseModel):
    """
    Data to create/update a Course.
    'level' is optional to allow graceful evolution if migration not yet applied.
    """
    id: Optional[int] = None
    level: Optional[str] = None
class CourseOut(BaseModel):
    id: int
    level: Optional[str] = None
class EnrollmentIn(BaseModel):
    """
    Data to create/update an Enrollment relationship between a Student and a Course.
    """
    id: Optional[int] = None
    student_id: int
    course_id: int
class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
class TeacherIn(BaseModel):
    id: Optional[int] = None
class TeacherOut(BaseModel):
    id: int
class TeachingIn(BaseModel):
    id: Optional[int] = None
    teacher_id: int
    course_id: int
class TeachingOut(BaseModel):
    id: int
    teacher_id: int
    course_id: int