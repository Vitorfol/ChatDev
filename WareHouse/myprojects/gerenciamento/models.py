'''
Domain models for Student, Teacher, and ClassRoom.
Each model includes helper methods to convert to/from dict for storage.
'''
from dataclasses import dataclass, field
from typing import List, Dict, Any
@dataclass
class Student:
    id: int = None
    name: str = ''
    age: int = 0
    email: str = ''
    teachers: List[int] = field(default_factory=list)
    classes: List[int] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'email': self.email,
            'teachers': list(self.teachers),
            'classes': list(self.classes)
        }
    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> 'Student':
        return Student(
            id=obj.get('id'),
            name=obj.get('name', ''),
            age=int(obj.get('age', 0)) if obj.get('age') is not None else 0,
            email=obj.get('email', ''),
            teachers=list(obj.get('teachers', [])),
            classes=list(obj.get('classes', []))
        )
@dataclass
class Teacher:
    id: int = None
    name: str = ''
    subject: str = ''
    email: str = ''
    students: List[int] = field(default_factory=list)
    classes: List[int] = field(default_factory=list)
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'email': self.email,
            'students': list(self.students),
            'classes': list(self.classes)
        }
    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> 'Teacher':
        return Teacher(
            id=obj.get('id'),
            name=obj.get('name', ''),
            subject=obj.get('subject', ''),
            email=obj.get('email', ''),
            students=list(obj.get('students', [])),
            classes=list(obj.get('classes', []))
        )
@dataclass
class ClassRoom:
    id: int = None
    name: str = ''
    teacher_id: int = None
    students: List[int] = field(default_factory=list)
    schedule: List[Dict[str, str]] = field(default_factory=list)  # e.g., [{"day":"Mon","time":"10:00-11:00"}]
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'teacher_id': self.teacher_id,
            'students': list(self.students),
            'schedule': list(self.schedule)
        }
    @staticmethod
    def from_dict(obj: Dict[str, Any]) -> 'ClassRoom':
        return ClassRoom(
            id=obj.get('id'),
            name=obj.get('name', ''),
            teacher_id=obj.get('teacher_id'),
            students=list(obj.get('students', [])),
            schedule=list(obj.get('schedule', []))
        )