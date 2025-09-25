'''
SQLAlchemy ORM models: Student, Course, Teacher and the association table for many-to-many
relationship between students and courses.
'''
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
# Association table for many-to-many Student <-> Course
student_course_association = Table(
    "student_course_association",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    courses = relationship(
        "Course",
        secondary=student_course_association,
        back_populates="students",
        lazy="joined",
    )
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    courses = relationship("Course", back_populates="teacher", cascade="all, delete")
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    level = Column(Integer, nullable=False, default=100)  # level attribute added
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="courses", lazy="joined")
    students = relationship(
        "Student",
        secondary=student_course_association,
        back_populates="courses",
        lazy="joined",
    )