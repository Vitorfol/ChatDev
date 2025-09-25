'''
CRUD utility functions for Student, Course, and Teacher entities. These functions
encapsulate database operations used by the API routers.
'''
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import models
import schemas
# Student CRUD
def create_student(db: Session, student_in: schemas.StudentCreate) -> models.Student:
    student = models.Student(name=student_in.name, email=student_in.email)
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(student)
    return student
def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()
def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()
def update_student(db: Session, student_id: int, updates: schemas.StudentUpdate) -> Optional[models.Student]:
    student = get_student(db, student_id)
    if not student:
        return None
    if updates.name is not None:
        student.name = updates.name
    if updates.email is not None:
        student.email = updates.email
    db.add(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(student)
    return student
def delete_student(db: Session, student_id: int) -> bool:
    student = get_student(db, student_id)
    if not student:
        return False
    db.delete(student)
    db.commit()
    return True
def enroll_student_in_course(db: Session, student_id: int, course_id: int) -> bool:
    student = get_student(db, student_id)
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not student or not course:
        return False
    if course not in student.courses:
        student.courses.append(course)
        db.add(student)
        db.commit()
        db.refresh(student)
    return True
def unenroll_student_from_course(db: Session, student_id: int, course_id: int) -> bool:
    student = get_student(db, student_id)
    course = db.query(models.Course).filter(models.Course.id == course_id).first()
    if not student or not course:
        return False
    if course in student.courses:
        student.courses.remove(course)
        db.add(student)
        db.commit()
    return True
# Teacher CRUD
def create_teacher(db: Session, teacher_in: schemas.TeacherCreate) -> models.Teacher:
    teacher = models.Teacher(name=teacher_in.name)
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
def get_teacher(db: Session, teacher_id: int) -> Optional[models.Teacher]:
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
def get_teachers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    return db.query(models.Teacher).offset(skip).limit(limit).all()
def update_teacher(db: Session, teacher_id: int, updates: schemas.TeacherUpdate) -> Optional[models.Teacher]:
    teacher = get_teacher(db, teacher_id)
    if not teacher:
        return None
    if updates.name is not None:
        teacher.name = updates.name
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher
def delete_teacher(db: Session, teacher_id: int) -> bool:
    teacher = get_teacher(db, teacher_id)
    if not teacher:
        return False
    db.delete(teacher)
    db.commit()
    return True
# Course CRUD
def create_course(db: Session, course_in: schemas.CourseCreate) -> Optional[models.Course]:
    course = models.Course(title=course_in.title, level=course_in.level)
    if course_in.teacher_id is not None:
        teacher = get_teacher(db, course_in.teacher_id)
        if not teacher:
            return None
        course.teacher = teacher
    db.add(course)
    db.commit()
    db.refresh(course)
    return course
def get_course(db: Session, course_id: int) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.id == course_id).first()
def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    return db.query(models.Course).offset(skip).limit(limit).all()
def update_course(db: Session, course_id: int, updates: schemas.CourseUpdate) -> Optional[models.Course]:
    course = get_course(db, course_id)
    if not course:
        return None
    if updates.title is not None:
        course.title = updates.title
    if updates.level is not None:
        course.level = updates.level
    # If updates.teacher_id is provided (including None), we treat only explicit ints as change.
    if updates.teacher_id is not None:
        # allow setting to a specific teacher; if teacher_id is invalid, return None to signal error
        teacher = get_teacher(db, updates.teacher_id)
        if not teacher:
            return None
        course.teacher = teacher
    # Note: If updates.teacher_id is omitted (i.e., None in the schema), do not change teacher.
    db.add(course)
    db.commit()
    db.refresh(course)
    return course
def delete_course(db: Session, course_id: int) -> bool:
    course = get_course(db, course_id)
    if not course:
        return False
    db.delete(course)
    db.commit()
    return True
def get_students_in_course(db: Session, course_id: int) -> Optional[List[models.Student]]:
    course = get_course(db, course_id)
    if not course:
        return None
    return course.students