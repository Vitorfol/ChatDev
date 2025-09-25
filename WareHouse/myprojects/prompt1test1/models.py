'''
SQLAlchemy models: Student, Teacher, Course and the association table for enrollments.
'''
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
# Association table for many-to-many between students and courses
enrollments_table = Table(
    "enrollments",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)
class Student(Base):
    """
    Student model with id, name, email, and relationship to courses.
    """
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    courses = relationship(
        "Course",
        secondary=enrollments_table,
        back_populates="students",
        lazy="joined"
    )
class Teacher(Base):
    """
    Teacher model with id, name, and relationship to courses.
    """
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    courses = relationship("Course", back_populates="teacher", cascade="all,delete", lazy="joined")
class Course(Base):
    """
    Course model with id, title, level, optional teacher_id, and relationships.
    """
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    level = Column(String, index=True, nullable=False)  # e.g., 'beginner', 'intermediate', 'advanced'
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="courses", lazy="joined")
    students = relationship(
        "Student",
        secondary=enrollments_table,
        back_populates="courses",
        lazy="joined"
    )