'''
Repository layer abstracts direct DB operations using SQLAlchemy sessions.
Provides CRUD for students, courses, teachers, and operations for enrollments and teachings.
'''
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import schemas
from sqlalchemy.exc import IntegrityError
# Student repository
class StudentRepository:
    def __init__(self, db: Session):
        self.db = db
    def create(self, student_in: schemas.StudentCreate) -> models.Student:
        student = models.Student(name=student_in.name, email=student_in.email)
        self.db.add(student)
        try:
            self.db.commit()
            self.db.refresh(student)
            return student
        except IntegrityError:
            self.db.rollback()
            raise
    def get(self, student_id: int) -> Optional[models.Student]:
        return self.db.query(models.Student).filter(models.Student.id == student_id).first()
    def list(self, skip: int = 0, limit: int = 100) -> List[models.Student]:
        return self.db.query(models.Student).offset(skip).limit(limit).all()
    def update(self, student: models.Student, updates: schemas.StudentUpdate) -> models.Student:
        if updates.name is not None:
            student.name = updates.name
        if updates.email is not None:
            student.email = updates.email
        try:
            self.db.commit()
            self.db.refresh(student)
            return student
        except IntegrityError:
            self.db.rollback()
            raise
    def delete(self, student: models.Student) -> None:
        self.db.delete(student)
        self.db.commit()
# Course repository
class CourseRepository:
    def __init__(self, db: Session):
        self.db = db
    def create(self, course_in: schemas.CourseCreate) -> models.Course:
        course = models.Course(title=course_in.title, level=course_in.level)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course
    def get(self, course_id: int) -> Optional[models.Course]:
        return self.db.query(models.Course).filter(models.Course.id == course_id).first()
    def list(self, skip: int = 0, limit: int = 100) -> List[models.Course]:
        return self.db.query(models.Course).offset(skip).limit(limit).all()
    def update(self, course: models.Course, updates: schemas.CourseUpdate) -> models.Course:
        if updates.title is not None:
            course.title = updates.title
        if updates.level is not None:
            course.level = updates.level
        self.db.commit()
        self.db.refresh(course)
        return course
    def delete(self, course: models.Course) -> None:
        self.db.delete(course)
        self.db.commit()
# Teacher repository
class TeacherRepository:
    def __init__(self, db: Session):
        self.db = db
    def create(self, teacher_in: schemas.TeacherCreate) -> models.Teacher:
        teacher = models.Teacher(name=teacher_in.name, department=teacher_in.department)
        self.db.add(teacher)
        self.db.commit()
        self.db.refresh(teacher)
        return teacher
    def get(self, teacher_id: int) -> Optional[models.Teacher]:
        return self.db.query(models.Teacher).filter(models.Teacher.id == teacher_id).first()
    def list(self, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
        return self.db.query(models.Teacher).offset(skip).limit(limit).all()
    def update(self, teacher: models.Teacher, updates: schemas.TeacherUpdate) -> models.Teacher:
        if updates.name is not None:
            teacher.name = updates.name
        if updates.department is not None:
            teacher.department = updates.department
        self.db.commit()
        self.db.refresh(teacher)
        return teacher
    def delete(self, teacher: models.Teacher) -> None:
        self.db.delete(teacher)
        self.db.commit()
# Enrollment repository (association)
class EnrollmentRepository:
    def __init__(self, db: Session):
        self.db = db
    def list(self) -> List[dict]:
        rows = self.db.execute("SELECT student_id, course_id FROM enrollments;").fetchall()
        return [{"student_id": r[0], "course_id": r[1]} for r in rows]
    def create(self, student_id: int, course_id: int) -> None:
        # Use raw insert to respect composite PK
        try:
            self.db.execute(
                "INSERT INTO enrollments (student_id, course_id) VALUES (:s, :c);",
                {"s": student_id, "c": course_id},
            )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
    def delete(self, student_id: int, course_id: int) -> None:
        self.db.execute(
            "DELETE FROM enrollments WHERE student_id = :s AND course_id = :c;",
            {"s": student_id, "c": course_id},
        )
        self.db.commit()
# Teaching repository (association)
class TeachingRepository:
    def __init__(self, db: Session):
        self.db = db
    def list(self) -> List[dict]:
        rows = self.db.execute("SELECT teacher_id, course_id FROM teachings;").fetchall()
        return [{"teacher_id": r[0], "course_id": r[1]} for r in rows]
    def create(self, teacher_id: int, course_id: int) -> None:
        try:
            self.db.execute(
                "INSERT INTO teachings (teacher_id, course_id) VALUES (:t, :c);",
                {"t": teacher_id, "c": course_id},
            )
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise
    def delete(self, teacher_id: int, course_id: int) -> None:
        self.db.execute(
            "DELETE FROM teachings WHERE teacher_id = :t AND course_id = :c;",
            {"t": teacher_id, "c": course_id},
        )
        self.db.commit()