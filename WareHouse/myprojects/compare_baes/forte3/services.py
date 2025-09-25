'''
Service layer that coordinates repositories and applies domain rules.
The service functions call repositories and provide higher-level operations used by API handlers.
'''
from typing import Optional, List, Dict
from repositories import StudentRepository, CourseRepository, EnrollmentRepository, TeacherRepository, TeachingRepository
from domain.entities import StudentIn, CourseIn, EnrollmentIn, TeacherIn, TeachingIn
student_repo = StudentRepository()
course_repo = CourseRepository()
enrollment_repo = EnrollmentRepository()
teacher_repo = TeacherRepository()
teaching_repo = TeachingRepository()
class StudentService:
    """
    Domain service for student operations.
    """
    def create(self, data: StudentIn) -> Dict:
        return student_repo.create(data)
    def get(self, id: int) -> Optional[Dict]:
        return student_repo.get(id)
    def list(self) -> List[Dict]:
        return student_repo.list_all()
    def update(self, id: int, data: StudentIn) -> Optional[Dict]:
        return student_repo.update(id, data)
    def delete(self, id: int) -> bool:
        return student_repo.delete(id)
class CourseService:
    def create(self, data: CourseIn) -> Dict:
        return course_repo.create(data)
    def get(self, id: int) -> Optional[Dict]:
        return course_repo.get(id)
    def list(self) -> List[Dict]:
        return course_repo.list_all()
    def update(self, id: int, data: CourseIn) -> Optional[Dict]:
        return course_repo.update(id, data)
    def delete(self, id: int) -> bool:
        return course_repo.delete(id)
class EnrollmentService:
    def create(self, data: EnrollmentIn) -> Dict:
        # Basic validation: ensure student and course exist
        s = student_repo.get(data.student_id)
        c = course_repo.get(data.course_id)
        if s is None:
            raise RuntimeError("student does not exist")
        if c is None:
            raise RuntimeError("course does not exist")
        return enrollment_repo.create(data)
    def get(self, id: int) -> Optional[Dict]:
        return enrollment_repo.get(id)
    def list(self) -> List[Dict]:
        return enrollment_repo.list_all()
    def update(self, id: int, data: EnrollmentIn) -> Optional[Dict]:
        return enrollment_repo.update(id, data)
    def delete(self, id: int) -> bool:
        return enrollment_repo.delete(id)
class TeacherService:
    def create(self, data: TeacherIn) -> Dict:
        return teacher_repo.create(data)
    def get(self, id: int) -> Optional[Dict]:
        return teacher_repo.get(id)
    def list(self) -> List[Dict]:
        return teacher_repo.list_all()
    def delete(self, id: int) -> bool:
        return teacher_repo.delete(id)
class TeachingService:
    def create(self, data: TeachingIn) -> Dict:
        # Validate teacher and course exist
        t = teacher_repo.get(data.teacher_id)
        c = course_repo.get(data.course_id)
        if t is None:
            raise RuntimeError("teacher does not exist")
        if c is None:
            raise RuntimeError("course does not exist")
        return teaching_repo.create(data)
    def get(self, id: int) -> Optional[Dict]:
        return teaching_repo.get(id)
    def list(self) -> List[Dict]:
        return teaching_repo.list_all()
    def update(self, id: int, data: TeachingIn) -> Optional[Dict]:
        return teaching_repo.update(id, data)
    def delete(self, id: int) -> bool:
        return teaching_repo.delete(id)