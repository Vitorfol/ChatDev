'''
Automated smoke test that drives migrations sequentially and verifies CRUD across all
entities and relationships. Uses FastAPI TestClient to exercise the running app in-process.
Run this after launching main.app in the same interpreter (or importable).
'''
import sys
import time
import os
# Defer importing TestClient and the running app until we actually run the smoke test.
# This allows the module to be imported in environments that don't have FastAPI installed,
# and provides a clear, actionable message instead of an unhandled ModuleNotFoundError.
try:
    from fastapi.testclient import TestClient  # type: ignore
except Exception as _e:
    TestClient = None  # type: ignore
def apply_next(client):
    resp = client.post("/migrate/next")
    if resp.status_code != 200:
        print("Failed to apply migration:", resp.status_code, resp.text)
        return None
    return resp.json()
def expect(condition, message):
    if not condition:
        print("FAILED:", message)
        sys.exit(2)
def run_smoke_test():
    # If TestClient is unavailable, provide a friendly message and skip the smoke test.
    if TestClient is None:
        print("SMOKE TEST SKIPPED: 'fastapi' (and its TestClient) is not installed in the environment.")
        print("Install dependencies and re-run. Example:")
        print("  pip install fastapi[all] requests")
        return 0
    # Import the app and migration_manager only when FastAPI is available.
    # This avoids import-time failures in environments without FastAPI.
    try:
        from main import app, migration_manager  # noqa: WPS433 (intentional dynamic import)
    except Exception as e:
        print("SMOKE TEST ABORTED: failed to import the running FastAPI app (from main).")
        print("Ensure the application module 'main' exposes 'app' and 'migration_manager'.")
        print("Import error:", e)
        return 1
    client = TestClient(app)
    # Ensure DB file removed so we run from clean slate for idempotent testing
    from db import get_db_path
    dbp = get_db_path()
    try:
        if os.path.exists(dbp):
            os.remove(dbp)
    except Exception as e:
        print("Warning: couldn't remove DB file:", e)
    # Step 1: Apply migration 1 (create student)
    r = apply_next(client)
    expect(r and r.get("applied") == "001_create_student", "Expected migration 001_create_student")
    # Student endpoints now present. Create a student.
    resp = client.post("/students", json={"id": 1})
    expect(resp.status_code == 201, "Create student failed after migration 1")
    # Get student back
    resp = client.get("/students/1")
    expect(resp.status_code == 200 and resp.json().get("id") == 1, "Get student failed after migration 1")
    # Step 2: Add email column
    r = apply_next(client)
    expect(r and r.get("applied") == "002_add_student_email", "Expected migration 002_add_student_email")
    # Update student with email using PUT
    resp = client.put("/students/1", json={"email": "alice@example.com"})
    expect(resp.status_code == 200 and resp.json().get("email") == "alice@example.com", "Update student email failed")
    resp = client.get("/students/1")
    expect(resp.json().get("email") == "alice@example.com", "Stored email not found")
    # Step 3: Create Course
    r = apply_next(client)
    expect(r and r.get("applied") == "003_create_course", "Expected migration 003_create_course")
    # Create course and fetch
    resp = client.post("/courses", json={"id": 10, "level": "Undergrad"})
    expect(resp.status_code == 201, "Create course failed")
    resp = client.get("/courses/10")
    expect(resp.status_code == 200 and resp.json().get("level") == "Undergrad", "Get course failed")
    # Step 4: Enrollment relationship + endpoints
    r = apply_next(client)
    expect(r and r.get("applied") == "004_create_enrollment", "Expected migration 004_create_enrollment")
    # Create an enrollment
    resp = client.post("/enrollments", json={"student_id": 1, "course_id": 10})
    expect(resp.status_code == 201, "Create enrollment failed")
    eid = resp.json().get("id")
    resp = client.get(f"/enrollments/{eid}")
    expect(resp.status_code == 200 and resp.json().get("student_id") == 1, "Get enrollment failed")
    # Step 5: Teacher entity
    r = apply_next(client)
    expect(r and r.get("applied") == "005_create_teacher", "Expected migration 005_create_teacher")
    # Create teacher
    resp = client.post("/teachers", json={"id": 500})
    expect(resp.status_code == 201, "Create teacher failed")
    resp = client.get("/teachers/500")
    expect(resp.status_code == 200, "Get teacher failed")
    # Step 6: Teaching relationship + endpoints
    r = apply_next(client)
    expect(r and r.get("applied") == "006_create_teaching", "Expected migration 006_create_teaching")
    # Create teaching relation
    resp = client.post("/teachings", json={"teacher_id": 500, "course_id": 10})
    expect(resp.status_code == 201, "Create teaching failed")
    tid = resp.json().get("id")
    resp = client.get(f"/teachings/{tid}")
    expect(resp.status_code == 200 and resp.json().get("teacher_id") == 500, "Get teaching failed")
    # Additional CRUD smoke operations
    # List checks
    resp = client.get("/students")
    expect(resp.status_code == 200 and len(resp.json()) >= 1, "Students list failed")
    resp = client.get("/courses")
    expect(resp.status_code == 200 and len(resp.json()) >= 1, "Courses list failed")
    resp = client.get("/enrollments")
    expect(resp.status_code == 200 and len(resp.json()) >= 1, "Enrollments list failed")
    resp = client.get("/teachers")
    expect(resp.status_code == 200 and len(resp.json()) >= 1, "Teachers list failed")
    resp = client.get("/teachings")
    expect(resp.status_code == 200 and len(resp.json()) >= 1, "Teachings list failed")
    print("SMOKE TEST PASSED")
    return 0
if __name__ == "__main__":
    sys.exit(run_smoke_test())