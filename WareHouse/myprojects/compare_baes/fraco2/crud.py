'''
CRUD helper functions to interact with the database via SQLAlchemy ORM.
Implements create/read/update/delete for Student, Course, Teacher and relationship operations.
'''
from sqlalchemy.orm import Session
from typing import List
import models
import schemas
# ----- Student CRUD -----
def get_student(db: Session, student_id: int):
    return db.query(models.Student).filter(models.Student.id == student_id).first()
def get_student_by_email(db: Session, email: str):
    return db.query(models.Student).filter(models.Student.email == email).first()
def get_students(db: Session, skip: int = 0, limit: int = 100) -> List[models.Student]:
    return db.query(models.Student).offset(skip).limit(limit).all()
def create_student(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(name=student.name, email=str(student.email))
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
def update_student(db: Session, db_student: models.Student, student_update: schemas.StudentUpdate) -> models.Student:
    if student_update.name is not None:
        db_student.name = student_update.name
    if student_update.email is not None:
        db_student.email = str(student_update.email)
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student
def delete_student(db: Session, db_student: models.Student):
    # Remove associations first (not strictly necessary with SQLite + cascade not set)
    db_student.courses = []
    db.delete(db_student)
    db.commit()
# ----- Teacher CRUD -----
def get_teacher(db: Session, teacher_id: int):
    return db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
def get_teacher_by_email(db: Session, email: str):
    return db.query(models.Teacher).filter(models.Teacher.email == email).first()
def get_teachers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
    return db.query(models.Teacher).offset(skip).limit(limit).all()
def create_teacher(db: Session, teacher: schemas.TeacherCreate) -> models.Teacher:
    db_teacher = models.Teacher(name=teacher.name, email=str(teacher.email) if teacher.email else None)
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
def update_teacher(db: Session, db_teacher: models.Teacher, teacher_update: schemas.TeacherUpdate) -> models.Teacher:
    if teacher_update.name is not None:
        db_teacher.name = teacher_update.name
    if teacher_update.email is not None:
        db_teacher.email = teacher_update.email
    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)
    return db_teacher
def delete_teacher(db: Session, db_teacher: models.Teacher):
    # Unassign teacher from any courses
    for course in db_teacher.courses:
        course.teacher = None
    db.delete(db_teacher)
    db.commit()
def get_courses_for_teacher(db: Session, teacher: models.Teacher):
    return teacher.courses
# ----- Course CRUD -----
def get_course(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()
def get_courses(db: Session, skip: int = 0, limit: int = 100) -> List[models.Course]:
    return db.query(models.Course).offset(skip).limit(limit).all()
def create_course(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(title=course.title, description=course.description, level=course.level)
    if course.teacher_id:
        teacher = get_teacher(db, teacher_id=course.teacher_id)
        if not teacher:
            raise ValueError("Teacher not found")
        db_course.teacher = teacher
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
def update_course(db: Session, db_course: models.Course, course_update: schemas.CourseUpdate) -> models.Course:
    if course_update.title is not None:
        db_course.title = course_update.title
    if course_update.description is not None:
        db_course.description = course_update.description
    if course_update.level is not None:
        db_course.level = course_update.level
    if course_update.teacher_id is not None:
        if course_update.teacher_id == 0:
            # Unassign
            db_course.teacher = None
        else:
            teacher = get_teacher(db, teacher_id=course_update.teacher_id)
            if not teacher:
                raise ValueError("Teacher not found")
            db_course.teacher = teacher
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course
def delete_course(db: Session, db_course: models.Course):
    # Remove student associations first
    db_course.students = []
    db.delete(db_course)
    db.commit()
def assign_teacher_to_course(db: Session, course: models.Course, teacher: models.Teacher) -> models.Course:
    course.teacher = teacher
    db.add(course)
    db.commit()
    db.refresh(course)
    return course
# ----- Student-Course relationships -----
def enroll_student_in_course(db: Session, student: models.Student, course: models.Course) -> models.Student:
    if course in student.courses:
        # Already enrolled
        return student
    student.courses.append(course)
    db.add(student)
    db.commit()
    db.refresh(student)
    return student
def remove_student_from_course(db: Session, student: models.Student, course: models.Course) -> models.Student:
    if course in student.courses:
        student.courses.remove(course)
        db.add(student)
        db.commit()
        db.refresh(student)
    return student
def get_courses_for_student(db: Session, student: models.Student):
    return student.courses
def get_students_in_course(db: Session, course: models.Course):
    return course.students