'''
Domain services that sit between the API and the repositories.
They preserve semantic vocabulary and docstrings for entities and operations.
'''
from typing import List, Optional, Dict, Any
import repositories as repo
# Student service
def create_student(id: int, email: Optional[str] = None) -> None:
    """
    Create a Student entity with id and optional email.
    """
    repo.create_student(id=id, email=email)
def get_student(id: int) -> Optional[Dict[str, Any]]:
    return repo.get_student(id)
def list_students() -> List[Dict[str, Any]]:
    return repo.list_students()
def update_student(id: int, email: Optional[str]) -> bool:
    return repo.update_student(id, email)
def delete_student(id: int) -> bool:
    return repo.delete_student(id)
# Course service
def create_course(id: int, level: Optional[str] = None) -> None:
    repo.create_course(id=id, level=level)
def get_course(id: int) -> Optional[Dict[str, Any]]:
    return repo.get_course(id)
def list_courses() -> List[Dict[str, Any]]:
    return repo.list_courses()
def update_course(id: int, level: Optional[str]) -> bool:
    return repo.update_course(id, level)
def delete_course(id: int) -> bool:
    return repo.delete_course(id)
# Enrollment service
def create_enrollment(student_id: int, course_id: int) -> int:
    return repo.create_enrollment(student_id=student_id, course_id=course_id)
def get_enrollment(id: int) -> Optional[Dict[str, Any]]:
    return repo.get_enrollment(id)
def list_enrollments() -> List[Dict[str, Any]]:
    return repo.list_enrollments()
def delete_enrollment(id: int) -> bool:
    return repo.delete_enrollment(id)
# Teacher service
def create_teacher(id: int) -> None:
    repo.create_teacher(id=id)
def get_teacher(id: int) -> Optional[Dict[str, Any]]:
    return repo.get_teacher(id)
def list_teachers() -> List[Dict[str, Any]]:
    return repo.list_teachers()
def delete_teacher(id: int) -> bool:
    return repo.delete_teacher(id)
# Teaching service
def create_teaching(teacher_id: int, course_id: int) -> int:
    return repo.create_teaching(teacher_id=teacher_id, course_id=course_id)
def get_teaching(id: int) -> Optional[Dict[str, Any]]:
    return repo.get_teaching(id)
def list_teachings() -> List[Dict[str, Any]]:
    return repo.list_teachings()
def delete_teaching(id: int) -> bool:
    return repo.delete_teaching(id)