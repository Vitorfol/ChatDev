'''
Service layer implementing business operations and coordinating repositories.
Services hide repository details from the API layer and maintain semantic
vocabulary and docstrings.
'''
from db import SessionLocal
from repositories import (
    StudentRepository, CourseRepository, TeacherRepository,
    EnrollmentRepository, TeachingRepository, RepositoryError
)
from models import Student, Course, Teacher, Enrollment, Teaching
class ServiceError(Exception):
    pass
class StudentService:
    """Business operations for Student aggregate."""
    def __init__(self):
        self._Session = SessionLocal
    def create_student(self, id: int, email: str | None = None):
        """
        Create a Student aggregate.
        Returns the created Student ORM instance or raises ServiceError on failure.
        """
        with self._Session() as s:
            repo = StudentRepository(s)
            student = Student(id=id, email=email)
            try:
                return repo.create(student)
            except RepositoryError as e:
                raise ServiceError(str(e))
    def get_student(self, id: int):
        """Retrieve a Student by id or return None if not found."""
        with self._Session() as s:
            return StudentRepository(s).get(id)
    def list_students(self):
        """List all Students."""
        with self._Session() as s:
            return StudentRepository(s).list()
    def update_student(self, id: int, email: str | None = None):
        """
        Update fields on a Student. Returns updated Student or None if not found.
        """
        with self._Session() as s:
            return StudentRepository(s).update(id, email=email)
    def delete_student(self, id: int):
        """Delete a Student by id. Returns True if deleted, False if not found."""
        with self._Session() as s:
            return StudentRepository(s).delete(id)
class CourseService:
    """Business operations for Course aggregate."""
    def __init__(self):
        self._Session = SessionLocal
    def create_course(self, id: int, level: str | None = None):
        """Create a Course aggregate."""
        with self._Session() as s:
            try:
                return CourseRepository(s).create(Course(id=id, level=level))
            except RepositoryError as e:
                raise ServiceError(str(e))
    def get_course(self, id: int):
        """Retrieve a Course by id or return None if not found."""
        with self._Session() as s:
            return CourseRepository(s).get(id)
    def list_courses(self):
        """List all Courses."""
        with self._Session() as s:
            return CourseRepository(s).list()
    def update_course(self, id: int, level: str | None = None):
        """Update Course fields. Returns updated Course or None if not found."""
        with self._Session() as s:
            return CourseRepository(s).update(id, level=level)
    def delete_course(self, id: int):
        """Delete a Course by id. Returns True if deleted, False if not found."""
        with self._Session() as s:
            return CourseRepository(s).delete(id)
class TeacherService:
    """Business operations for Teacher aggregate."""
    def __init__(self):
        self._Session = SessionLocal
    def create_teacher(self, id: int):
        """Create a Teacher aggregate."""
        with self._Session() as s:
            try:
                return TeacherRepository(s).create(Teacher(id=id))
            except RepositoryError as e:
                raise ServiceError(str(e))
    def get_teacher(self, id: int):
        """Retrieve a Teacher by id or return None if not found."""
        with self._Session() as s:
            return TeacherRepository(s).get(id)
    def list_teachers(self):
        """List all Teachers."""
        with self._Session() as s:
            return TeacherRepository(s).list()
    def delete_teacher(self, id: int):
        """Delete a Teacher by id. Returns True if deleted, False if not found."""
        with self._Session() as s:
            return TeacherRepository(s).delete(id)
class EnrollmentService:
    """Operations for Enrollment association."""
    def __init__(self):
        self._Session = SessionLocal
    def create_enrollment(self, student_id: int, course_id: int):
        """
        Create an Enrollment association between Student and Course.
        Raises ServiceError on repository-level errors (e.g., missing tables or FK violations).
        """
        with self._Session() as s:
            try:
                e = Enrollment(student_id=student_id, course_id=course_id)
                return EnrollmentRepository(s).create(e)
            except RepositoryError as err:
                raise ServiceError(str(err))
    def list_enrollments(self):
        """List all Enrollment associations."""
        with self._Session() as s:
            return EnrollmentRepository(s).list()
    def get_enrollment(self, id: int):
        """Retrieve an Enrollment by id or return None if not found."""
        with self._Session() as s:
            return EnrollmentRepository(s).get(id)
    def delete_enrollment(self, id: int):
        """Delete an Enrollment by id. Returns True if deleted, False if not found."""
        with self._Session() as s:
            return EnrollmentRepository(s).delete(id)
class TeachingService:
    """Operations for Teaching association."""
    def __init__(self):
        self._Session = SessionLocal
    def create_teaching(self, teacher_id: int, course_id: int):
        """
        Create a Teaching association between Teacher and Course.
        Raises ServiceError on repository-level errors (e.g., missing tables or FK violations).
        """
        with self._Session() as s:
            try:
                t = Teaching(teacher_id=teacher_id, course_id=course_id)
                return TeachingRepository(s).create(t)
            except RepositoryError as err:
                raise ServiceError(str(err))
    def list_teachings(self):
        """List all Teaching associations."""
        with self._Session() as s:
            return TeachingRepository(s).list()
    def get_teaching(self, id: int):
        """Retrieve a Teaching by id or return None if not found."""
        with self._Session() as s:
            return TeachingRepository(s).get(id)
    def delete_teaching(self, id: int):
        """Delete a Teaching by id. Returns True if deleted, False if not found."""
        with self._Session() as s:
            return TeachingRepository(s).delete(id)