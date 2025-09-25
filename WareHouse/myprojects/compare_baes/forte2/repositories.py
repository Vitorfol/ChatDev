'''
Repository layer providing atomic DB operations for each aggregate.
Each repository receives a SQLAlchemy session and offers CRUD operations.
They are resilient to missing tables (raise informative exceptions).
'''
from sqlalchemy.exc import OperationalError, IntegrityError
from sqlalchemy import select
from db import SessionLocal
from models import Student, Course, Teacher, Enrollment, Teaching
class RepositoryError(Exception):
    pass
class StudentRepository:
    """Repository for Student aggregate."""
    def __init__(self, session):
        self.session = session
    def create(self, student: Student):
        try:
            self.session.add(student)
            self.session.commit()
            self.session.refresh(student)
            return student
        except OperationalError as e:
            self.session.rollback()
            raise RepositoryError("students table might not exist yet") from e
        except IntegrityError as e:
            self.session.rollback()
            raise RepositoryError("student create failed: IntegrityError") from e
    def get(self, student_id: int):
        return self.session.get(Student, student_id)
    def list(self):
        return self.session.scalars(select(Student)).all()
    def update(self, student_id: int, **fields):
        student = self.get(student_id)
        if not student:
            return None
        for k, v in fields.items():
            setattr(student, k, v)
        self.session.commit()
        self.session.refresh(student)
        return student
    def delete(self, student_id: int):
        student = self.get(student_id)
        if not student:
            return False
        self.session.delete(student)
        self.session.commit()
        return True
class CourseRepository:
    """Repository for Course aggregate."""
    def __init__(self, session):
        self.session = session
    def create(self, course: Course):
        try:
            self.session.add(course)
            self.session.commit()
            self.session.refresh(course)
            return course
        except OperationalError as e:
            self.session.rollback()
            raise RepositoryError("courses table might not exist yet") from e
    def get(self, course_id: int):
        return self.session.get(Course, course_id)
    def list(self):
        return self.session.scalars(select(Course)).all()
    def update(self, course_id: int, **fields):
        course = self.get(course_id)
        if not course:
            return None
        for k, v in fields.items():
            setattr(course, k, v)
        self.session.commit()
        self.session.refresh(course)
        return course
    def delete(self, course_id: int):
        course = self.get(course_id)
        if not course:
            return False
        self.session.delete(course)
        self.session.commit()
        return True
class TeacherRepository:
    """Repository for Teacher aggregate."""
    def __init__(self, session):
        self.session = session
    def create(self, teacher: Teacher):
        try:
            self.session.add(teacher)
            self.session.commit()
            self.session.refresh(teacher)
            return teacher
        except OperationalError as e:
            self.session.rollback()
            raise RepositoryError("teachers table might not exist yet") from e
    def get(self, teacher_id: int):
        return self.session.get(Teacher, teacher_id)
    def list(self):
        return self.session.scalars(select(Teacher)).all()
    def delete(self, teacher_id: int):
        teacher = self.get(teacher_id)
        if not teacher:
            return False
        self.session.delete(teacher)
        self.session.commit()
        return True
class EnrollmentRepository:
    """Repository for Enrollment association."""
    def __init__(self, session):
        self.session = session
    def create(self, enrollment: Enrollment):
        try:
            self.session.add(enrollment)
            self.session.commit()
            self.session.refresh(enrollment)
            return enrollment
        except OperationalError as e:
            self.session.rollback()
            raise RepositoryError("enrollments (or referenced tables) might not exist yet") from e
        except IntegrityError as e:
            self.session.rollback()
            raise RepositoryError("enrollment create failed: IntegrityError") from e
    def get(self, enrollment_id: int):
        return self.session.get(Enrollment, enrollment_id)
    def list(self):
        return self.session.scalars(select(Enrollment)).all()
    def delete(self, enrollment_id: int):
        e = self.get(enrollment_id)
        if not e:
            return False
        self.session.delete(e)
        self.session.commit()
        return True
class TeachingRepository:
    """Repository for Teaching association."""
    def __init__(self, session):
        self.session = session
    def create(self, teaching: Teaching):
        try:
            self.session.add(teaching)
            self.session.commit()
            self.session.refresh(teaching)
            return teaching
        except OperationalError as e:
            self.session.rollback()
            raise RepositoryError("teachings (or referenced tables) might not exist yet") from e
        except IntegrityError as e:
            self.session.rollback()
            raise RepositoryError("teaching create failed: IntegrityError") from e
    def get(self, teaching_id: int):
        return self.session.get(Teaching, teaching_id)
    def list(self):
        return self.session.scalars(select(Teaching)).all()
    def delete(self, teaching_id: int):
        t = self.get(teaching_id)
        if not t:
            return False
        self.session.delete(t)
        self.session.commit()
        return True