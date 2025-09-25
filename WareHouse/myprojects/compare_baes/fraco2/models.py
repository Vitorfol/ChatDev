'''
SQLAlchemy ORM models for Student, Course, Teacher, and association table for many-to-many.
'''
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from database import Base
# Association table for many-to-many Student <-> Course
student_course_association = Table(
    "student_course",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=False)
    courses = relationship("Course", secondary=student_course_association, back_populates="students")
    def __repr__(self):
        return f"<Student id={self.id} name={self.name} email={self.email}>"
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, index=True, nullable=True)
    courses = relationship("Course", back_populates="teacher")
    def __repr__(self):
        return f"<Teacher id={self.id} name={self.name} email={self.email}>"
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(String(50), nullable=True)  # e.g., "Beginner", "Intermediate", "Advanced"
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    teacher = relationship("Teacher", back_populates="courses")
    students = relationship("Student", secondary=student_course_association, back_populates="courses")
    def __repr__(self):
        return f"<Course id={self.id} title={self.title} level={self.level} teacher_id={self.teacher_id}>"