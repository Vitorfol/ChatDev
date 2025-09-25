'''
Service layer encapsulates business logic and orchestrates repositories.
This is where domain rules (e.g., unique email) are enforced.
'''
from sqlalchemy.orm import Session
from typing import List
import repositories
import schemas
import models
from sqlalchemy.exc import IntegrityError
class StudentService:
    def __init__(self, db: Session):
        self.repo = repositories.StudentRepository(db)
    def create_student(self, student_in: schemas.StudentCreate) -> models.Student:
        # Enforce unique email at service level for nicer errors (DB also enforces)
        existing = self.repo.db.query(models.Student).filter(models.Student.email == student_in.email).first()
        if existing:
            raise ValueError(f"Email {student_in.email} is already used by student id {existing.id}")
        try:
            return self.repo.create(student_in)
        except IntegrityError:
            raise ValueError("Could not create student due to integrity error.")
    def get_student(self, student_id: int) -> models.Student:
        student = self.repo.get(student_id)
        if not student:
            raise LookupError("Student not found")
        return student
    def list_students(self, skip: int = 0, limit: int = 100) -> List[models.Student]:
        return self.repo.list(skip=skip, limit=limit)
    def update_student(self, student_id: int, updates: schemas.StudentUpdate) -> models.Student:
        student = self.repo.get(student_id)
        if not student:
            raise LookupError("Student not found")
        # if updating email, ensure uniqueness
        if updates.email:
            other = self.repo.db.query(models.Student).filter(models.Student.email == updates.email, models.Student.id != student_id).first()
            if other:
                raise ValueError("Email already in use by another student")
        try:
            return self.repo.update(student, updates)
        except IntegrityError:
            raise ValueError("Could not update student due to integrity error.")
    def delete_student(self, student_id: int) -> None:
        student = self.repo.get(student_id)
        if not student:
            raise LookupError("Student not found")
        self.repo.delete(student)
class CourseService:
    def __init__(self, db: Session):
        self.repo = repositories.CourseRepository(db)
    def create_course(self, course_in: schemas.CourseCreate) -> models.Course:
        return self.repo.create(course_in)
    def get_course(self, course_id: int) -> models.Course:
        course = self.repo.get(course_id)
        if not course:
            raise LookupError("Course not found")
        return course
    def list_courses(self, skip: int = 0, limit: int = 100) -> List[models.Course]:
        return self.repo.list(skip=skip, limit=limit)
    def update_course(self, course_id: int, updates: schemas.CourseUpdate) -> models.Course:
        course = self.repo.get(course_id)
        if not course:
            raise LookupError("Course not found")
        return self.repo.update(course, updates)
    def delete_course(self, course_id: int) -> None:
        course = self.repo.get(course_id)
        if not course:
            raise LookupError("Course not found")
        self.repo.delete(course)
class TeacherService:
    def __init__(self, db: Session):
        self.repo = repositories.TeacherRepository(db)
    def create_teacher(self, teacher_in: schemas.TeacherCreate) -> models.Teacher:
        return self.repo.create(teacher_in)
    def get_teacher(self, teacher_id: int) -> models.Teacher:
        teacher = self.repo.get(teacher_id)
        if not teacher:
            raise LookupError("Teacher not found")
        return teacher
    def list_teachers(self, skip: int = 0, limit: int = 100) -> List[models.Teacher]:
        return self.repo.list(skip=skip, limit=limit)
    def update_teacher(self, teacher_id: int, updates: schemas.TeacherUpdate) -> models.Teacher:
        teacher = self.repo.get(teacher_id)
        if not teacher:
            raise LookupError("Teacher not found")
        return self.repo.update(teacher, updates)
    def delete_teacher(self, teacher_id: int) -> None:
        teacher = self.repo.get(teacher_id)
        if not teacher:
            raise LookupError("Teacher not found")
        self.repo.delete(teacher)
class EnrollmentService:
    def __init__(self, db: Session):
        self.repo = repositories.EnrollmentRepository(db)
        self.student_repo = repositories.StudentRepository(db)
        self.course_repo = repositories.CourseRepository(db)
    def list_enrollments(self):
        return self.repo.list()
    def enroll(self, student_id: int, course_id: int) -> None:
        student = self.student_repo.get(student_id)
        if not student:
            raise LookupError("Student not found")
        course = self.course_repo.get(course_id)
        if not course:
            raise LookupError("Course not found")
        try:
            self.repo.create(student_id, course_id)
        except IntegrityError:
            raise ValueError("Enrollment already exists or invalid")
    def unenroll(self, student_id: int, course_id: int) -> None:
        self.repo.delete(student_id, course_id)
class TeachingService:
    def __init__(self, db: Session):
        self.repo = repositories.TeachingRepository(db)
        self.teacher_repo = repositories.TeacherRepository(db)
        self.course_repo = repositories.CourseRepository(db)
    def list_teachings(self):
        return self.repo.list()
    def assign(self, teacher_id: int, course_id: int) -> None:
        teacher = self.teacher_repo.get(teacher_id)
        if not teacher:
            raise LookupError("Teacher not found")
        course = self.course_repo.get(course_id)
        if not course:
            raise LookupError("Course not found")
        try:
            self.repo.create(teacher_id, course_id)
        except IntegrityError:
            raise ValueError("Teaching assignment already exists or invalid")
    def unassign(self, teacher_id: int, course_id: int) -> None:
        self.repo.delete(teacher_id, course_id)