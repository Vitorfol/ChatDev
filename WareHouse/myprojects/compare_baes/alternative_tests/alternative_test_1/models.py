'''
SQLAlchemy ORM models that map to the database tables created by migrations.
Defines Student, Course, Enrollment, Teacher, and CourseTeacher models.
'''
'''
SQLAlchemy ORM models that map to the database tables created by migrations.
Defines Student, Course, Enrollment, Teacher, and CourseTeacher models.
'''
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
Base = declarative_base()
class Student(Base):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    enrollments = relationship("Enrollment", back_populates="student", cascade="all, delete-orphan")
    courses = relationship("Course", secondary="enrollment", back_populates="students")
class Course(Base):
    __tablename__ = "course"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    level = Column(String, nullable=True)
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    students = relationship("Student", secondary="enrollment", back_populates="courses")
    course_teachers = relationship("CourseTeacher", back_populates="course", cascade="all, delete-orphan")
    teachers = relationship("Teacher", secondary="course_teacher", back_populates="courses")
class Enrollment(Base):
    __tablename__ = "enrollment"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    student_id = Column(Integer, ForeignKey("student.id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint("student_id", "course_id", name="uix_student_course"),)
    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
class Teacher(Base):
    __tablename__ = "teacher"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    department = Column(String, nullable=True)
    course_teachers = relationship("CourseTeacher", back_populates="teacher", cascade="all, delete-orphan")
    courses = relationship("Course", secondary="course_teacher", back_populates="teachers")
class CourseTeacher(Base):
    __tablename__ = "course_teacher"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey("course.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teacher.id", ondelete="CASCADE"), nullable=False)
    __table_args__ = (UniqueConstraint("course_id", "teacher_id", name="uix_course_teacher"),)
    course = relationship("Course", back_populates="course_teachers")
    teacher = relationship("Teacher", back_populates="course_teachers")