'''
Domain entities and Pydantic schemas.
This file defines SQLAlchemy ORM models for Student, Course, Teacher,
Enrollment, and Teaching, as well as Pydantic models used for request/response
validation. ORM models match the final schema after all migrations, but the
migration manager will create/alter DB objects incrementally.
'''
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db import Base
from pydantic import BaseModel
from typing import Optional
# ------------------ ORM models (final shape) ------------------
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    email = Column(String, nullable=True)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    # docstring preserved across evolution:
    """Student entity: identity and contact info."""
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    level = Column(String, nullable=True)
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    teachings = relationship("Teaching", back_populates="course", cascade="all, delete-orphan")
    """Course entity: offerings with a level attribute."""
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    teachings = relationship("Teaching", back_populates="teacher", cascade="all, delete-orphan")
    """Teacher entity: identity only (can be extended later)."""
class Enrollment(Base):
    __tablename__ = "enrollments"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="_student_course_uc"),)
    """Association: Student enrolled in Course."""
class Teaching(Base):
    __tablename__ = "teachings"
    id = Column(Integer, primary_key=True, index=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    teacher = relationship("Teacher", back_populates="teachings")
    course = relationship("Course", back_populates="teachings")
    __table_args__ = (UniqueConstraint("teacher_id", "course_id", name="_teacher_course_uc"),)
    """Association: Teacher teaches Course."""
# ------------------ Pydantic schemas ------------------
class StudentCreate(BaseModel):
    id: int
    email: Optional[str] = None
class StudentUpdate(BaseModel):
    email: Optional[str] = None
class StudentOut(BaseModel):
    id: int
    email: Optional[str] = None
    class Config:
        orm_mode = True
class CourseCreate(BaseModel):
    id: int
    level: Optional[str] = None
class CourseUpdate(BaseModel):
    level: Optional[str] = None
class CourseOut(BaseModel):
    id: int
    level: Optional[str] = None
    class Config:
        orm_mode = True
class TeacherCreate(BaseModel):
    id: int
class TeacherOut(BaseModel):
    id: int
    class Config:
        orm_mode = True
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int
class EnrollmentOut(BaseModel):
    id: int
    student_id: int
    course_id: int
    class Config:
        orm_mode = True
class TeachingCreate(BaseModel):
    teacher_id: int
    course_id: int
class TeachingOut(BaseModel):
    id: int
    teacher_id: int
    course_id: int
    class Config:
        orm_mode = True