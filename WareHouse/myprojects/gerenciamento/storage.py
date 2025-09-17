'''
Simple JSON-backed storage layer for students, teachers, and classes.
Implements CRUD-like operations and methods to create relationships:
- assign_teacher_to_student
- assign_student_to_class
- assign_teacher_to_class
Data is stored in a JSON file with structure:
{
  "next_ids": {"student": 1, "teacher": 1, "class": 1},
  "students": [...],
  "teachers": [...],
  "classes": [...]
}
This module is hardened to create parent directories when initializing the DB file.
'''
import json
import threading
from models import Student, Teacher, ClassRoom
import os
class Storage:
    def clear_all(self):
        """Remove todos os dados do banco (db.json) e reseta os IDs."""
        with self.lock:
            self._init_db()
    def __init__(self, filename):
        self.filename = filename
        self.lock = threading.Lock()
        # Initialize file if missing
        if not os.path.exists(self.filename):
            self._init_db()
    def _init_db(self):
        # Ensure the parent directory exists before attempting to write the DB file.
        dirpath = os.path.dirname(self.filename)
        if dirpath:
            os.makedirs(dirpath, exist_ok=True)
        initial = {
            "next_ids": {"student": 1, "teacher": 1, "class": 1},
            "students": [],
            "teachers": [],
            "classes": []
        }
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(initial, f, indent=2)
    def ensure_initialized(self):
        if not os.path.exists(self.filename):
            self._init_db()
    def _read(self):
        with self.lock:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return json.load(f)
    def _write(self, payload):
        with self.lock:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(payload, f, indent=2)
    # Student operations
    def get_all_students(self):
        data = self._read()
        return data.get('students', [])
    def create_student(self, student: Student):
        data = self._read()
        sid = data['next_ids']['student']
        student.id = sid
        data['next_ids']['student'] = sid + 1
        data['students'].append(student.to_dict())
        # persist
        self._write(data)
        return student.to_dict()
    # Teacher operations
    def get_all_teachers(self):
        data = self._read()
        return data.get('teachers', [])
    def create_teacher(self, teacher: Teacher):
        data = self._read()
        tid = data['next_ids']['teacher']
        teacher.id = tid
        data['next_ids']['teacher'] = tid + 1
        data['teachers'].append(teacher.to_dict())
        self._write(data)
        return teacher.to_dict()
    # Class operations
    def get_all_classes(self):
        data = self._read()
        return data.get('classes', [])
    def create_class(self, classroom: ClassRoom):
        data = self._read()
        cid = data['next_ids']['class']
        classroom.id = cid
        data['next_ids']['class'] = cid + 1
        data['classes'].append(classroom.to_dict())
        self._write(data)
        return classroom.to_dict()
    # Relationship helpers
    def _find_student(self, data, student_id):
        for s in data['students']:
            if s['id'] == student_id:
                return s
        return None
    def _find_teacher(self, data, teacher_id):
        for t in data['teachers']:
            if t['id'] == teacher_id:
                return t
        return None
    def _find_class(self, data, class_id):
        for c in data['classes']:
            if c['id'] == class_id:
                return c
        return None
    def assign_teacher_to_student(self, student_id, teacher_id):
        data = self._read()
        student = self._find_student(data, student_id)
        teacher = self._find_teacher(data, teacher_id)
        if student is None:
            return False, f"Student with id {student_id} not found"
        if teacher is None:
            return False, f"Teacher with id {teacher_id} not found"
        # update student's teachers list
        if 'teachers' not in student:
            student['teachers'] = []
        if teacher_id not in student['teachers']:
            student['teachers'].append(teacher_id)
        # update teacher's students list
        if 'students' not in teacher:
            teacher['students'] = []
        if student_id not in teacher['students']:
            teacher['students'].append(student_id)
        self._write(data)
        return True, f"Teacher {teacher_id} assigned to student {student_id}"
    def assign_student_to_class(self, student_id, class_id):
        data = self._read()
        student = self._find_student(data, student_id)
        classroom = self._find_class(data, class_id)
        if student is None:
            return False, f"Student with id {student_id} not found"
        if classroom is None:
            return False, f"Class with id {class_id} not found"
        # update class students
        if 'students' not in classroom:
            classroom['students'] = []
        if student_id not in classroom['students']:
            classroom['students'].append(student_id)
        # update student's classes
        if 'classes' not in student:
            student['classes'] = []
        if class_id not in student['classes']:
            student['classes'].append(class_id)
        self._write(data)
        return True, f"Student {student_id} assigned to class {class_id}"
    def assign_teacher_to_class(self, teacher_id, class_id):
        data = self._read()
        teacher = self._find_teacher(data, teacher_id)
        classroom = self._find_class(data, class_id)
        if teacher is None:
            return False, f"Teacher with id {teacher_id} not found"
        if classroom is None:
            return False, f"Class with id {class_id} not found"
        # set class teacher
        classroom['teacher_id'] = teacher_id
        # update teacher's classes (optional)
        if 'classes' not in teacher:
            teacher['classes'] = []
        if class_id not in teacher['classes']:
            teacher['classes'].append(class_id)
        self._write(data)
        return True, f"Teacher {teacher_id} assigned to class {class_id}"