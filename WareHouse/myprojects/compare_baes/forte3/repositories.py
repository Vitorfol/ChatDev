'''
Repository layer: encapsulate data access using SQLAlchemy Core with dynamic reflection.
Repositories reflect the database schema at each operation, so they adapt to migrations
applied in-process without requiring ORM class redefinition or server restart.
'''
from typing import List, Optional, Dict, Any
from sqlalchemy import select, insert, update, delete, text
from sqlalchemy.engine import Row
from db import engine, reflect_table, table_exists, get_table_columns
from domain.entities import StudentIn, StudentOut, CourseIn, CourseOut, EnrollmentIn, EnrollmentOut, TeacherIn, TeacherOut, TeachingIn, TeachingOut
class BaseRepository:
    def _row_to_dict(self, row: Row) -> Dict[str, Any]:
        return dict(row._mapping)
class StudentRepository(BaseRepository):
    def create(self, student: StudentIn) -> Dict:
        if not table_exists("students"):
            raise RuntimeError("students table does not exist")
        students = reflect_table("students")
        data = {}
        if student.id is not None:
            data["id"] = student.id
        if student.email is not None and "email" in [c["name"] for c in get_table_columns("students")]:
            data["email"] = student.email
        with engine.begin() as conn:
            res = conn.execute(insert(students).values(**data))
            # SQLite: if id not provided, last_insert_rowid
            if student.id is None:
                new_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
            else:
                new_id = student.id
            row = conn.execute(select(students).where(students.c.id == new_id)).first()
            return self._row_to_dict(row)
    def get(self, id: int) -> Optional[Dict]:
        if not table_exists("students"):
            return None
        students = reflect_table("students")
        with engine.connect() as conn:
            row = conn.execute(select(students).where(students.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def list_all(self) -> List[Dict]:
        if not table_exists("students"):
            return []
        students = reflect_table("students")
        with engine.connect() as conn:
            rows = conn.execute(select(students)).all()
            return [self._row_to_dict(r) for r in rows]
    def update(self, id: int, student: StudentIn) -> Optional[Dict]:
        if not table_exists("students"):
            return None
        students = reflect_table("students")
        data = {}
        cols = [c["name"] for c in get_table_columns("students")]
        if student.email is not None and "email" in cols:
            data["email"] = student.email
        if not data:
            return self.get(id)
        with engine.begin() as conn:
            conn.execute(update(students).where(students.c.id == id).values(**data))
            row = conn.execute(select(students).where(students.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def delete(self, id: int) -> bool:
        if not table_exists("students"):
            return False
        students = reflect_table("students")
        with engine.begin() as conn:
            res = conn.execute(delete(students).where(students.c.id == id))
            return res.rowcount > 0
class CourseRepository(BaseRepository):
    def create(self, course: CourseIn) -> Dict:
        if not table_exists("courses"):
            raise RuntimeError("courses table does not exist")
        courses = reflect_table("courses")
        data = {}
        if course.id is not None:
            data["id"] = course.id
        if course.level is not None:
            data["level"] = course.level
        with engine.begin() as conn:
            res = conn.execute(insert(courses).values(**data))
            if course.id is None:
                new_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
            else:
                new_id = course.id
            row = conn.execute(select(courses).where(courses.c.id == new_id)).first()
            return self._row_to_dict(row)
    def get(self, id: int) -> Optional[Dict]:
        if not table_exists("courses"):
            return None
        courses = reflect_table("courses")
        with engine.connect() as conn:
            row = conn.execute(select(courses).where(courses.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def list_all(self) -> List[Dict]:
        if not table_exists("courses"):
            return []
        courses = reflect_table("courses")
        with engine.connect() as conn:
            rows = conn.execute(select(courses)).all()
            return [self._row_to_dict(r) for r in rows]
    def update(self, id: int, course: CourseIn) -> Optional[Dict]:
        if not table_exists("courses"):
            return None
        courses = reflect_table("courses")
        data = {}
        cols = [c["name"] for c in get_table_columns("courses")]
        if course.level is not None and "level" in cols:
            data["level"] = course.level
        if not data:
            return self.get(id)
        with engine.begin() as conn:
            conn.execute(update(courses).where(courses.c.id == id).values(**data))
            row = conn.execute(select(courses).where(courses.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def delete(self, id: int) -> bool:
        if not table_exists("courses"):
            return False
        courses = reflect_table("courses")
        with engine.begin() as conn:
            res = conn.execute(delete(courses).where(courses.c.id == id))
            return res.rowcount > 0
class EnrollmentRepository(BaseRepository):
    def create(self, enrollment: EnrollmentIn) -> Dict:
        if not table_exists("enrollments"):
            raise RuntimeError("enrollments table does not exist")
        enrollments = reflect_table("enrollments")
        data = {"student_id": enrollment.student_id, "course_id": enrollment.course_id}
        if enrollment.id is not None:
            data["id"] = enrollment.id
        with engine.begin() as conn:
            conn.execute(insert(enrollments).values(**data))
            if enrollment.id is None:
                new_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
            else:
                new_id = enrollment.id
            row = conn.execute(select(enrollments).where(enrollments.c.id == new_id)).first()
            return self._row_to_dict(row)
    def get(self, id: int) -> Optional[Dict]:
        if not table_exists("enrollments"):
            return None
        enrollments = reflect_table("enrollments")
        with engine.connect() as conn:
            row = conn.execute(select(enrollments).where(enrollments.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def list_all(self) -> List[Dict]:
        if not table_exists("enrollments"):
            return []
        enrollments = reflect_table("enrollments")
        with engine.connect() as conn:
            rows = conn.execute(select(enrollments)).all()
            return [self._row_to_dict(r) for r in rows]
    def update(self, id: int, enrollment: EnrollmentIn) -> Optional[Dict]:
        if not table_exists("enrollments"):
            return None
        enrollments = reflect_table("enrollments")
        data = {}
        if enrollment.student_id is not None:
            data["student_id"] = enrollment.student_id
        if enrollment.course_id is not None:
            data["course_id"] = enrollment.course_id
        if not data:
            return self.get(id)
        with engine.begin() as conn:
            conn.execute(update(enrollments).where(enrollments.c.id == id).values(**data))
            row = conn.execute(select(enrollments).where(enrollments.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def delete(self, id: int) -> bool:
        if not table_exists("enrollments"):
            return False
        enrollments = reflect_table("enrollments")
        with engine.begin() as conn:
            res = conn.execute(delete(enrollments).where(enrollments.c.id == id))
            return res.rowcount > 0
class TeacherRepository(BaseRepository):
    def create(self, teacher: TeacherIn) -> Dict:
        if not table_exists("teachers"):
            raise RuntimeError("teachers table does not exist")
        teachers = reflect_table("teachers")
        data = {}
        if teacher.id is not None:
            data["id"] = teacher.id
        with engine.begin() as conn:
            conn.execute(insert(teachers).values(**data))
            if teacher.id is None:
                new_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
            else:
                new_id = teacher.id
            row = conn.execute(select(teachers).where(teachers.c.id == new_id)).first()
            return self._row_to_dict(row)
    def get(self, id: int) -> Optional[Dict]:
        if not table_exists("teachers"):
            return None
        teachers = reflect_table("teachers")
        with engine.connect() as conn:
            row = conn.execute(select(teachers).where(teachers.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def list_all(self) -> List[Dict]:
        if not table_exists("teachers"):
            return []
        teachers = reflect_table("teachers")
        with engine.connect() as conn:
            rows = conn.execute(select(teachers)).all()
            return [self._row_to_dict(r) for r in rows]
    def update(self, id: int, teacher: TeacherIn) -> Optional[Dict]:
        # No extra fields yet; nothing to update besides id which is PK.
        return self.get(id)
    def delete(self, id: int) -> bool:
        if not table_exists("teachers"):
            return False
        teachers = reflect_table("teachers")
        with engine.begin() as conn:
            res = conn.execute(delete(teachers).where(teachers.c.id == id))
            return res.rowcount > 0
class TeachingRepository(BaseRepository):
    def create(self, teaching: TeachingIn) -> Dict:
        if not table_exists("teachings"):
            raise RuntimeError("teachings table does not exist")
        teachings = reflect_table("teachings")
        data = {"teacher_id": teaching.teacher_id, "course_id": teaching.course_id}
        if teaching.id is not None:
            data["id"] = teaching.id
        with engine.begin() as conn:
            conn.execute(insert(teachings).values(**data))
            if teaching.id is None:
                new_id = conn.execute(text("SELECT last_insert_rowid()")).scalar()
            else:
                new_id = teaching.id
            row = conn.execute(select(teachings).where(teachings.c.id == new_id)).first()
            return self._row_to_dict(row)
    def get(self, id: int) -> Optional[Dict]:
        if not table_exists("teachings"):
            return None
        teachings = reflect_table("teachings")
        with engine.connect() as conn:
            row = conn.execute(select(teachings).where(teachings.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def list_all(self) -> List[Dict]:
        if not table_exists("teachings"):
            return []
        teachings = reflect_table("teachings")
        with engine.connect() as conn:
            rows = conn.execute(select(teachings)).all()
            return [self._row_to_dict(r) for r in rows]
    def update(self, id: int, teaching: TeachingIn) -> Optional[Dict]:
        if not table_exists("teachings"):
            return None
        teachings = reflect_table("teachings")
        data = {}
        if teaching.teacher_id is not None:
            data["teacher_id"] = teaching.teacher_id
        if teaching.course_id is not None:
            data["course_id"] = teaching.course_id
        if not data:
            return self.get(id)
        with engine.begin() as conn:
            conn.execute(update(teachings).where(teachings.c.id == id).values(**data))
            row = conn.execute(select(teachings).where(teachings.c.id == id)).first()
            return self._row_to_dict(row) if row else None
    def delete(self, id: int) -> bool:
        if not table_exists("teachings"):
            return False
        teachings = reflect_table("teachings")
        with engine.begin() as conn:
            res = conn.execute(delete(teachings).where(teachings.c.id == id))
            return res.rowcount > 0