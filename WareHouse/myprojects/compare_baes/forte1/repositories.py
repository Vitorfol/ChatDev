'''
Repository layer: direct SQL access to SQLite using sqlite3.
Each function will raise RuntimeError with a helpful message if the underlying table
does not exist yet (i.e., the corresponding migration has not been applied).
'''
from typing import List, Optional, Dict, Any
import sqlite3
from db import connect_db
def table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    return cur.fetchone() is not None
# --- Student repository ---
def create_student(id: int, email: Optional[str] = None) -> None:
    conn = connect_db()
    try:
        if not table_exists(conn, "student"):
            raise RuntimeError("Student table does not exist. Apply migration 1.")
        cur = conn.cursor()
        cur.execute("INSERT INTO student (id, email) VALUES (?, ?);", (id, email))
        conn.commit()
    finally:
        conn.close()
def get_student(id: int) -> Optional[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "student"):
            raise RuntimeError("Student table does not exist. Apply migration 1.")
        cur = conn.execute("SELECT id, email FROM student WHERE id = ?;", (id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
def list_students() -> List[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "student"):
            raise RuntimeError("Student table does not exist. Apply migration 1.")
        cur = conn.execute("SELECT id, email FROM student;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
def update_student(id: int, email: Optional[str]) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "student"):
            raise RuntimeError("Student table does not exist. Apply migration 1.")
        cur = conn.execute("UPDATE student SET email = ? WHERE id = ?;", (email, id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
def delete_student(id: int) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "student"):
            raise RuntimeError("Student table does not exist. Apply migration 1.")
        cur = conn.execute("DELETE FROM student WHERE id = ?;", (id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
# --- Course repository ---
def create_course(id: int, level: Optional[str] = None) -> None:
    conn = connect_db()
    try:
        if not table_exists(conn, "course"):
            raise RuntimeError("Course table does not exist. Apply migration 3.")
        conn.execute("INSERT INTO course (id, level) VALUES (?, ?);", (id, level))
        conn.commit()
    finally:
        conn.close()
def get_course(id: int) -> Optional[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "course"):
            raise RuntimeError("Course table does not exist. Apply migration 3.")
        cur = conn.execute("SELECT id, level FROM course WHERE id = ?;", (id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
def list_courses() -> List[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "course"):
            raise RuntimeError("Course table does not exist. Apply migration 3.")
        cur = conn.execute("SELECT id, level FROM course;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
def update_course(id: int, level: Optional[str]) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "course"):
            raise RuntimeError("Course table does not exist. Apply migration 3.")
        cur = conn.execute("UPDATE course SET level = ? WHERE id = ?;", (level, id))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
def delete_course(id: int) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "course"):
            raise RuntimeError("Course table does not exist. Apply migration 3.")
        cur = conn.execute("DELETE FROM course WHERE id = ?;", (id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
# --- Enrollment repository ---
def create_enrollment(student_id: int, course_id: int) -> int:
    conn = connect_db()
    try:
        if not table_exists(conn, "enrollment"):
            raise RuntimeError("Enrollment table does not exist. Apply migration 4.")
        cur = conn.execute("INSERT INTO enrollment (student_id, course_id) VALUES (?, ?);", (student_id, course_id))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
def get_enrollment(id: int) -> Optional[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "enrollment"):
            raise RuntimeError("Enrollment table does not exist. Apply migration 4.")
        cur = conn.execute("SELECT id, student_id, course_id FROM enrollment WHERE id = ?;", (id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
def list_enrollments() -> List[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "enrollment"):
            raise RuntimeError("Enrollment table does not exist. Apply migration 4.")
        cur = conn.execute("SELECT id, student_id, course_id FROM enrollment;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
def delete_enrollment(id: int) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "enrollment"):
            raise RuntimeError("Enrollment table does not exist. Apply migration 4.")
        cur = conn.execute("DELETE FROM enrollment WHERE id = ?;", (id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
# --- Teacher repository ---
def create_teacher(id: int) -> None:
    conn = connect_db()
    try:
        if not table_exists(conn, "teacher"):
            raise RuntimeError("Teacher table does not exist. Apply migration 5.")
        conn.execute("INSERT INTO teacher (id) VALUES (?);", (id,))
        conn.commit()
    finally:
        conn.close()
def get_teacher(id: int) -> Optional[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "teacher"):
            raise RuntimeError("Teacher table does not exist. Apply migration 5.")
        cur = conn.execute("SELECT id FROM teacher WHERE id = ?;", (id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
def list_teachers() -> List[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "teacher"):
            raise RuntimeError("Teacher table does not exist. Apply migration 5.")
        cur = conn.execute("SELECT id FROM teacher;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
def delete_teacher(id: int) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "teacher"):
            raise RuntimeError("Teacher table does not exist. Apply migration 5.")
        cur = conn.execute("DELETE FROM teacher WHERE id = ?;", (id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()
# --- Teaching repository ---
def create_teaching(teacher_id: int, course_id: int) -> int:
    conn = connect_db()
    try:
        if not table_exists(conn, "teaching"):
            raise RuntimeError("Teaching table does not exist. Apply migration 6.")
        cur = conn.execute("INSERT INTO teaching (teacher_id, course_id) VALUES (?, ?);", (teacher_id, course_id))
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()
def get_teaching(id: int) -> Optional[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "teaching"):
            raise RuntimeError("Teaching table does not exist. Apply migration 6.")
        cur = conn.execute("SELECT id, teacher_id, course_id FROM teaching WHERE id = ?;", (id,))
        row = cur.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
def list_teachings() -> List[Dict[str, Any]]:
    conn = connect_db()
    try:
        if not table_exists(conn, "teaching"):
            raise RuntimeError("Teaching table does not exist. Apply migration 6.")
        cur = conn.execute("SELECT id, teacher_id, course_id FROM teaching;")
        return [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()
def delete_teaching(id: int) -> bool:
    conn = connect_db()
    try:
        if not table_exists(conn, "teaching"):
            raise RuntimeError("Teaching table does not exist. Apply migration 6.")
        cur = conn.execute("DELETE FROM teaching WHERE id = ?;", (id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()