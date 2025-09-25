'''
CRUD utility functions interacting with the database via SQLAlchemy ORM.
'''
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
# --------------------
# Student CRUD
# --------------------
def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    """
    Create and persist a Student.
    """
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        # Likely duplicate email
        raise e
    db.refresh(db_student)
    return db_student
def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    """
    Retrieve a student by ID.
    """
    return db.query(models.Student).filter(models.Student.id == student_id).first()
def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    """
    Retrieve multiple students.
    """
    return db.query(models.Student).offset(skip).limit(limit).all()
def update_student(db: Session, db_student: models.Student, updates: schemas.StudentUpdate) -> models.Student:
    """
    Update student attributes and commit.
    """
    if updates.name is not None:
        db_student.name = updates.name
    if updates.email is not None:
        db_student.email = updates.email
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
def delete_student(db: Session, db_student: models.Student) -> models.Student:
    """
    Delete a student.
    """
    db.delete(db_student)
    db.commit()
    return db_student
# --------------------
# Teacher CRUD
# --------------------
def create_teacher(db: Session, teacher: schemas.TeacherCreate) -> models.Teacher:
    """
    Create a new teacher.
    """
    db_teacher = models.Teacher(name=teacher.name)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
def get_teacher(db: Session, teacher_id: int) -> Optional[models.Teacher]:
    """
    Retrieve a teacher by ID.
    """
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
def get_teachers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    """
    Retrieve multiple teachers.
    """
    return db.query(models.Teacher).offset(skip).limit(limit).all()
def update_teacher(db: Session, db_teacher: models.Teacher, updates: schemas.TeacherUpdate) -> models.Teacher:
    """
    Update teacher fields.
    """
    if updates.name is not None:
        db_teacher.name = updates.name
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
def delete_teacher(db: Session, db_teacher: models.Teacher) -> models.Teacher:
    """
    Delete a teacher. Courses with this teacher will have teacher_id set to NULL due to cascade settings.
    """
    # Optionally unset teacher on courses first (SQLAlchemy handles relationship cascades).
    db.delete(db_teacher)
    db.commit()
    return db_teacher
# --------------------
# Course CRUD
# --------------------
def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    """
    Create a course and optionally link to a teacher.
    """
    db_course = models.Course(title=course.title, level=course.level, teacher_id=course.teacher_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    """
    Retrieve a course by ID.
    """
    return db.query(models.Course).filter(models.Course.id == course_id).first()
def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    """
    Retrieve multiple courses.
    """
    return db.query(models.Course).offset(skip).limit(limit).all()
def update_course(db: Session, db_course: models.Course, updates: schemas.CourseUpdate) -> models.Course:
    """
    Update course fields.
    """
    if updates.title is not None:
        db_course.title = updates.title
    if updates.level is not None:
        db_course.level = updates.level
    # teacher_id may be None to remove teacher
    if updates.teacher_id is not None:
        db_course.teacher_id = updates.teacher_id
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
def delete_course(db: Session, db_course: models.Course) -> models.Course:
    """
    Delete a course.
    """
    db.delete(db_course)
    db.commit()
    return db_course
# --------------------
# Enrollment / Relationships
# --------------------
def enroll_student_in_course(db: Session, course: models.Course, student: models.Student) -> models.Course:
    """
    Add student to course if not already enrolled.
    """
    if student not in course.students:
        course.students.append(student)
        db.add(course)
        db.commit()
        db.refresh(course)
    return course
def unenroll_student_from_course(db: Session, course: models.Course, student: models.Student) -> models.Course:
    """
    Remove student from course if enrolled.
    """
    if student in course.students:
        course.students.remove(student)
        db.add(course)
        db.commit()
        db.refresh(course)
    return course
def get_students_in_course(db: Session, course: models.Course) -> List[models.Student]:
    """
    Return list of students enrolled in a course.
    """
    # course.students is loaded via relationship
    return course.students
def get_courses_for_student(db: Session, student: models.Student) -> List[models.Course]:
    """
    Return list of courses a student is enrolled in.
    """
    return student.courses