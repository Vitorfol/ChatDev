'''
CRUD utility functions that operate on the SQLAlchemy models.
Each function encapsulates DB operations used by the FastAPI endpoints.
'''
from sqlalchemy.orm import Session
import models
import schemas
from typing import List, Optional
# Student operations
def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()
def get_student_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email == email).first()
def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()
def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(name=student.name, email=student.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
def update_student(db: Session, student_id: int, student: schemas.StudentUpdate) -> models.Student:
    db_student = get_student(db, student_id)
    if not db_student:
        raise ValueError("Student not found")
    # Only apply fields provided by client
    update_data = student.dict(exclude_unset=True)
    if "name" in update_data:
        db_student.name = update_data["name"]
    if "email" in update_data:
        db_student.email = update_data["email"]
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
def delete_student(db: Session, student_id: int) -> None:
    db_student = get_student(db, student_id)
    if db_student:
        db.delete(db_student)
        db.commit()
def enroll_student(db: Session, student_id: int, course_id: int) -> models.Student:
    student = get_student(db, student_id)
    if not student:
        raise ValueError("Student not found")
    course = get_course(db, course_id)
    if not course:
        raise ValueError("Course not found")
    if course not in student.courses:
        student.courses.append(course)
        db.add(student)
        db.commit()
        db.refresh(student)
    return student
def remove_student_from_course(db: Session, student_id: int, course_id: int) -> models.Student:
    student = get_student(db, student_id)
    if not student:
        raise ValueError("Student not found")
    course = get_course(db, course_id)
    if not course:
        raise ValueError("Course not found")
    if course in student.courses:
        student.courses.remove(course)
        db.add(student)
        db.commit()
        db.refresh(student)
    return student
# Course operations
def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.id == course_id).first()
def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    return db.query(models.Course).offset(skip).limit(limit).all()
def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(title=course.title, level=course.level, teacher_id=course.teacher_id)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
def update_course(db: Session, course_id: int, course: schemas.CourseUpdate) -> models.Course:
    db_course = get_course(db, course_id)
    if not db_course:
        raise ValueError("Course not found")
    # Only update fields that were actually provided by the client
    update_data = course.dict(exclude_unset=True)
    if "title" in update_data:
        db_course.title = update_data["title"]
    if "level" in update_data:
        db_course.level = update_data["level"]
    # If the client included teacher_id in the payload (even if explicitly null),
    # update the DB accordingly. If it was omitted, leave as-is.
    if "teacher_id" in update_data:
        db_course.teacher_id = update_data["teacher_id"]
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
def delete_course(db: Session, course_id: int) -> None:
    db_course = get_course(db, course_id)
    if db_course:
        db.delete(db_course)
        db.commit()
# Teacher operations
def get_teacher(db: Session, teacher_id: int) -> Optional[models.Teacher]:
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
def get_teachers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    return db.query(models.Teacher).offset(skip).limit(limit).all()
def create_teacher(db: Session, teacher: schemas.TeacherCreate) -> models.Teacher:
    db_teacher = models.Teacher(name=teacher.name, email=teacher.email)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
def update_teacher(db: Session, teacher_id: int, teacher: schemas.TeacherUpdate) -> models.Teacher:
    db_teacher = get_teacher(db, teacher_id)
    if not db_teacher:
        raise ValueError("Teacher not found")
    update_data = teacher.dict(exclude_unset=True)
    if "name" in update_data:
        db_teacher.name = update_data["name"]
    if "email" in update_data:
        db_teacher.email = update_data["email"]
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
def delete_teacher(db: Session, teacher_id: int) -> None:
    db_teacher = get_teacher(db, teacher_id)
    if db_teacher:
        # Rely on the database ON DELETE SET NULL and passive_deletes=True on the relationship.
        # Deleting the teacher will issue a DELETE; the DB will set related courses' teacher_id to NULL.
        db.delete(db_teacher)
        db.commit()