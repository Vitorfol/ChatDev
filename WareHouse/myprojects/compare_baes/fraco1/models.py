'''
SQLAlchemy models for Students, Courses, Teachers, and the association table.
Relationships:
- student_courses: association table for many-to-many Student <-> Course
- Student.courses <-> Course.students
- Teacher.courses (one-to-many) with DB-level ON DELETE SET NULL behavior
'''
from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship, declarative_base
Base = declarative_base()
# Association table for many-to-many relationship between students and courses
student_courses = Table(
    "student_courses",
    Base.metadata,
    Column("student_id", Integer, ForeignKey("students.id", ondelete="CASCADE"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id", ondelete="CASCADE"), primary_key=True),
)
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    courses = relationship("Course", secondary=student_courses, back_populates="students")
    def __repr__(self):
        return f"<Student id={self.id} name={self.name} email={self.email}>"
class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    # IMPORTANT: Do NOT use delete-orphan here. We want DB ON DELETE behavior (SET NULL)
    # to keep Course rows when a Teacher is deleted. Use passive_deletes=True and
    # do not cascade delete-orphan to avoid ORM-level deletion of courses.
    courses = relationship(
        "Course",
        back_populates="teacher",
        cascade="save-update, merge",   # keep normal persistence behavior but do NOT delete orphaned courses
        passive_deletes=True           # let the DB enforce ON DELETE behavior (SET NULL)
    )
    def __repr__(self):
        return f"<Teacher id={self.id} name={self.name} email={self.email}>"
class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    level = Column(String, nullable=True)  # e.g., beginner/intermediate/advanced
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    teacher = relationship("Teacher", back_populates="courses")
    students = relationship("Student", secondary=student_courses, back_populates="courses")
    def __repr__(self):
        return f"<Course id={self.id} title={self.title} level={self.level} teacher_id={self.teacher_id}>"