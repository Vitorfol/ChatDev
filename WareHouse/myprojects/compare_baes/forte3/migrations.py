'''
MigrationService implements zero-downtime, in-process migrations for the 6-step incremental evolution.
Each migration step is idempotent and recorded in the 'migrations' table.
Steps:
1. Create students(id PK)
2. Add students.email (TEXT)
3. Create courses(id PK, level TEXT)
4. Create enrollments(id PK, student_id FK, course_id FK)
5. Create teachers(id PK)
6. Create teachings(id PK, teacher_id FK, course_id FK)
'''
from typing import List, Tuple
from sqlalchemy import text
from db import engine, table_exists, get_table_columns, record_migration, get_applied_steps, ensure_migrations_table
from sqlalchemy.exc import OperationalError
MIGRATIONS = {
    1: ("create_students", "CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY)"),
    2: ("add_student_email", "ADD_COLUMN_EMAIL"),
    3: ("create_courses", "CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, level TEXT)"),
    4: ("create_enrollments", "CREATE TABLE IF NOT EXISTS enrollments (id INTEGER PRIMARY KEY, student_id INTEGER, course_id INTEGER, FOREIGN KEY(student_id) REFERENCES students(id), FOREIGN KEY(course_id) REFERENCES courses(id))"),
    5: ("create_teachers", "CREATE TABLE IF NOT EXISTS teachers (id INTEGER PRIMARY KEY)"),
    6: ("create_teachings", "CREATE TABLE IF NOT EXISTS teachings (id INTEGER PRIMARY KEY, teacher_id INTEGER, course_id INTEGER, FOREIGN KEY(teacher_id) REFERENCES teachers(id), FOREIGN KEY(course_id) REFERENCES courses(id))")
}
class MigrationService:
    def __init__(self):
        ensure_migrations_table()
    def apply_up_to(self, step: int) -> List[int]:
        """
        Apply migrations from the current state up to `step` inclusive.
        Returns a list of applied steps (including previously applied).
        """
        applied_before = set(get_applied_steps())
        applied_now = []
        for s in range(1, step + 1):
            if s in applied_before:
                continue
            self.apply_step(s)
            applied_now.append(s)
        return sorted(list(applied_before.union(set(applied_now))))
    def apply_step(self, step: int):
        if step not in MIGRATIONS:
            raise ValueError(f"No migration for step {step}")
        name, action = MIGRATIONS[step]
        with engine.begin() as conn:
            if step == 1:
                # Create students
                conn.execute(text(MIGRATIONS[1][1]))
            elif step == 2:
                # Add email column to students if not present
                # SQLite doesn't support IF NOT EXISTS for ADD COLUMN, so check pragma
                cols = get_table_columns("students")
                col_names = [c["name"] for c in cols]
                if "email" not in col_names:
                    conn.execute(text("ALTER TABLE students ADD COLUMN email TEXT"))
            elif step == 3:
                conn.execute(text(MIGRATIONS[3][1]))
            elif step == 4:
                conn.execute(text(MIGRATIONS[4][1]))
            elif step == 5:
                conn.execute(text(MIGRATIONS[5][1]))
            elif step == 6:
                conn.execute(text(MIGRATIONS[6][1]))
            else:
                raise ValueError(f"Unsupported migration step {step}")
            # Record migration
            record_migration(step, name)