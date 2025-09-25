'''
Migration manager implementing zero-downtime, in-process migrations.
Migrations are implemented as idempotent Python functions that manipulate the
SQLite schema via DDL. The manager records the applied version in the
'schema_versions' table so migrations can be applied incrementally without
restarting the server.
This revised version hardens ensure_version_table and current_version to:
- Use explicit transactions (engine.begin()) for initialization to ensure
  visibility/commit across connections.
- Use an idempotent INSERT ... WHERE NOT EXISTS to guarantee a single
  version row without DELETE gymnastics.
- Re-query using fresh connections after initialization to avoid stale
  connection visibility issues that led to None fetchone() results.
- Provide clearer error semantics if initialization fails.
'''
from sqlalchemy import text
from db import engine
from sqlalchemy.exc import OperationalError
import sqlite3
import logging
logger = logging.getLogger(__name__)
# We store version as a single-row table
VERSION_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS schema_versions (
    version INTEGER NOT NULL
);
"""
class MigrationManager:
    """
    Apply versioned migrations incrementally. Maintains semantic names and
    docstrings for each migration step for traceability.
    """
    def __init__(self, engine):
        self.engine = engine
        self.migrations = [
            self.migration_1_create_students_id,
            self.migration_2_add_student_email,
            self.migration_3_create_courses,
            self.migration_4_create_enrollments_association,
            self.migration_5_create_teachers,
            self.migration_6_create_teachings_association
        ]
    def ensure_version_table(self):
        """
        Ensure the schema_versions table exists and contains a single version row.
        This function is idempotent and uses an explicit transaction to make sure
        the inserted row is committed and visible to subsequent connections.
        """
        # Use a transaction so the CREATE TABLE and INSERT are atomic/committed
        with self.engine.begin() as conn:
            conn.execute(text(VERSION_TABLE_SQL))
            # Insert a single row with version=0 if no row exists. This is
            # idempotent and avoids race conditions from SELECT/DELETE/INSERT cycles.
            conn.execute(text("""
                INSERT INTO schema_versions(version)
                SELECT 0
                WHERE NOT EXISTS (SELECT 1 FROM schema_versions LIMIT 1);
            """))
    def current_version(self) -> int:
        """
        Return the current applied migration version.
        If the schema_versions table or row is missing, attempt to create/initialize it
        and re-query using a fresh connection. Raises RuntimeError if initialization
        does not yield a usable version row.
        """
        # First attempt using a fresh connection
        with self.engine.connect() as conn:
            try:
                r = conn.execute(text("SELECT version FROM schema_versions LIMIT 1")).fetchone()
            except Exception as e:
                logger.debug("current_version first-select failed: %s", e)
                r = None
        if r is None:
            # Try to initialize/create the version table and row using an explicit transaction
            try:
                self.ensure_version_table()
            except Exception as e:
                # If ensure fails, propagate a clear error
                logger.exception("Failed to ensure schema_versions table: %s", e)
                raise RuntimeError("Failed to initialize schema_versions table") from e
            # Re-query using a fresh connection to avoid any visibility/staleness problems
            with self.engine.connect() as conn2:
                r = conn2.execute(text("SELECT version FROM schema_versions LIMIT 1")).fetchone()
            if r is None:
                # If still none, raise a clear error instead of letting a TypeError occur
                logger.error("schema_versions table exists but contains no rows after initialization")
                raise RuntimeError("schema_versions table exists but contains no rows after initialization")
        # At this point r is expected to be a Row with index 0 holding an integer
        try:
            return int(r[0])
        except Exception as e:
            logger.exception("Invalid version value in schema_versions: %s", e)
            raise RuntimeError("Invalid version value in schema_versions") from e
    def set_version(self, v: int):
        """
        Update the stored schema version. Uses a short-lived connection to perform the update.
        """
        with self.engine.begin() as conn:
            conn.execute(text("UPDATE schema_versions SET version = :v"), {"v": v})
    def apply_next(self):
        cv = self.current_version()
        if cv >= len(self.migrations):
            return {"applied": False, "message": "No more migrations."}
        next_index = cv  # zero-based list; version stored is number applied
        migration_fn = self.migrations[next_index]
        migration_name = migration_fn.__name__
        # Execute migration
        try:
            migration_fn()
        except Exception as e:
            logger.exception("Migration %s failed: %s", migration_name, e)
            # Do not advance version if migration failed; return a clear payload
            return {"applied": False, "migration": migration_name, "error": str(e)}
        # Update version
        self.set_version(cv + 1)
        return {"applied": True, "migration": migration_name, "new_version": cv + 1}
    # ---------------- Migration implementations ----------------
    def migration_1_create_students_id(self):
        """
        Migration 1: Create Student entity table with id integer primary key.
        Preserves semantic entity name 'students'.
        """
        with self.engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY
            );
            """))
    def migration_2_add_student_email(self):
        """
        Migration 2: Add 'email' column (string) to students.
        SQLite supports ADD COLUMN; operation is idempotent.
        """
        # Check if column exists
        # Use sqlite3 directly to query PRAGMA; keep the same DB file path as engine
        try:
            db_path = engine.url.database or "academic.db"
        except Exception:
            db_path = "academic.db"
        with sqlite3.connect(db_path) as con:
            cur = con.execute("PRAGMA table_info(students);")
            cols = [row[1] for row in cur.fetchall()]
            if "email" not in cols:
                con.execute("ALTER TABLE students ADD COLUMN email TEXT;")
                con.commit()
    def migration_3_create_courses(self):
        """
        Migration 3: Create Course entity with id (PK) and level (string).
        """
        with self.engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY,
                level TEXT
            );
            """))
    def migration_4_create_enrollments_association(self):
        """
        Migration 4: Create enrollment relationship (enrollments) between Student and Course,
        with CRUD to be exposed by service layer.
        """
        with self.engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY(student_id) REFERENCES students(id),
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );
            """))
            # Create unique index to prevent duplicate enrollments
            conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_enrollment_student_course
            ON enrollments(student_id, course_id);
            """))
    def migration_5_create_teachers(self):
        """
        Migration 5: Create Teacher entity with id (PK).
        """
        with self.engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS teachers (
                id INTEGER PRIMARY KEY
            );
            """))
    def migration_6_create_teachings_association(self):
        """
        Migration 6: Create teaching relationship (teachings) between Teacher and Course,
        and later expose CRUD endpoints.
        """
        with self.engine.connect() as conn:
            conn.execute(text("""
            CREATE TABLE IF NOT EXISTS teachings (
                id INTEGER PRIMARY KEY,
                teacher_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY(teacher_id) REFERENCES teachers(id),
                FOREIGN KEY(course_id) REFERENCES courses(id)
            );
            """))
            conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ux_teaching_teacher_course
            ON teachings(teacher_id, course_id);
            """))
# Singleton manager instance
migration_manager = MigrationManager(engine)