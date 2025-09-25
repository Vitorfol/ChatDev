'''
Migration manager that applies an ordered set of in-process migrations.
Each migration is a function that operates directly on the SQLite file and, when
it should add API surface, calls app.include_router to mount the router at runtime.
Applied migrations are recorded in a simple migrations table to make migration
applications idempotent and inspectable.
'''
from typing import Callable, List, Dict, Any
import sqlite3
import os
from db import connect_db
from api import courses_router, enrollments_router, teachers_router, teachings_router
class MigrationManager:
    """
    Maintains an ordered list of migrations and supports applying them one at a time
    without restarting the FastAPI application. When migrations affect API surface,
    this manager mounts the relevant router on the app.
    """
    def __init__(self, app, db_path: str):
        self.app = app
        self.db_path = db_path
        self.migrations: List[Dict[str, Any]] = [
            {"name": "001_create_student", "func": self._m001_create_student},
            {"name": "002_add_student_email", "func": self._m002_add_student_email},
            {"name": "003_create_course", "func": self._m003_create_course},
            {"name": "004_create_enrollment", "func": self._m004_create_enrollment},
            {"name": "005_create_teacher", "func": self._m005_create_teacher},
            {"name": "006_create_teaching", "func": self._m006_create_teaching},
        ]
        self.ensure_migrations_table()
    def ensure_migrations_table(self):
        conn = connect_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    name TEXT PRIMARY KEY,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
        finally:
            conn.close()
    def get_applied_versions(self) -> List[str]:
        conn = connect_db()
        try:
            cur = conn.execute("SELECT name FROM migrations ORDER BY applied_at;")
            return [r["name"] for r in cur.fetchall()]
        finally:
            conn.close()
    def apply_next_migration(self) -> Dict[str, Any]:
        applied = set(self.get_applied_versions())
        for m in self.migrations:
            if m["name"] not in applied:
                # apply this migration
                m["func"]()
                # record
                conn = connect_db()
                try:
                    conn.execute("INSERT INTO migrations (name) VALUES (?);", (m["name"],))
                    conn.commit()
                finally:
                    conn.close()
                return {"applied": m["name"]}
        return {"applied": None, "message": "No pending migrations."}
    # --- migration implementations ---
    def _m001_create_student(self):
        """
        Create student table with id integer PK.
        """
        conn = connect_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS student (
                    id INTEGER PRIMARY KEY,
                    email TEXT
                );
            """)
            conn.commit()
        finally:
            conn.close()
    def _m002_add_student_email(self):
        """
        Add email column to student table (id already exists). This migration may run
        even if the column exists (idempotent).
        """
        conn = connect_db()
        try:
            # Check if column exists
            cur = conn.execute("PRAGMA table_info(student);")
            cols = [r["name"] for r in cur.fetchall()]
            if "email" not in cols:
                conn.execute("ALTER TABLE student ADD COLUMN email TEXT;")
                conn.commit()
        finally:
            conn.close()
    def _m003_create_course(self):
        """
        Create course table with id PK and level text. Also mounts the courses_router to the app.
        """
        conn = connect_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS course (
                    id INTEGER PRIMARY KEY,
                    level TEXT
                );
            """)
            conn.commit()
        finally:
            conn.close()
        # mount the courses router at runtime
        if not any(r.prefix == "/courses" for r in self.app.routes if hasattr(r, "path")):
            self.app.include_router(courses_router)
    def _m004_create_enrollment(self):
        """
        Create enrollment table referencing student and course, and mount the enrollment API.
        """
        conn = connect_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS enrollment (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    UNIQUE(student_id, course_id),
                    FOREIGN KEY(student_id) REFERENCES student(id) ON DELETE CASCADE,
                    FOREIGN KEY(course_id) REFERENCES course(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
        finally:
            conn.close()
        # mount enrollments router
        self.app.include_router(enrollments_router)
    def _m005_create_teacher(self):
        """
        Create teacher table and mount teachers router.
        """
        conn = connect_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teacher (
                    id INTEGER PRIMARY KEY
                );
            """)
            conn.commit()
        finally:
            conn.close()
        self.app.include_router(teachers_router)
    def _m006_create_teaching(self):
        """
        Create teaching table and mount teachings router.
        """
        conn = connect_db()
        try:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS teaching (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    teacher_id INTEGER NOT NULL,
                    course_id INTEGER NOT NULL,
                    UNIQUE(teacher_id, course_id),
                    FOREIGN KEY(teacher_id) REFERENCES teacher(id) ON DELETE CASCADE,
                    FOREIGN KEY(course_id) REFERENCES course(id) ON DELETE CASCADE
                );
            """)
            conn.commit()
        finally:
            conn.close()
        self.app.include_router(teachings_router)