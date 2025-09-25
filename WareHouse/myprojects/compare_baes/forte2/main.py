'''
Automated smoke test that sequentially applies migrations and verifies CRUD
for all entities and relationships.
Note: This file used to import "app" from itself (circular import) which caused
ImportError. It now imports the FastAPI app from the dedicated app.py module to
avoid circular imports and to provide a clear separation between the test
entrypoint and the application definition.
'''
from fastapi.testclient import TestClient
from app import app
from migrations import migration_manager
client = TestClient(app)
def apply_all_migrations():
    # Apply migrations sequentially
    results = []
    while True:
        res = client.post("/migrations/apply_next")
        j = res.json()
        results.append(j)
        if not j.get("applied", False):
            break
    return results
def run_smoke_test():
    # Reset DB file by re-running version table creation (handled by migration manager)
    migration_manager.ensure_version_table()
    # Apply migrations 1..6 sequentially
    apply_all_migrations()
    # After migrations, attempt CRUD sequences:
    # 1) Student CRUD
    r = client.post("/students", json={"id": 1, "email": "alice@example.com"})
    assert r.status_code == 200, f"Create student failed: {r.text}"
    r = client.get("/students/1")
    assert r.status_code == 200 and r.json()["email"] == "alice@example.com"
    # Update
    r = client.put("/students/1", json={"email": "alice2@example.com"})
    assert r.status_code == 200 and r.json()["email"] == "alice2@example.com"
    # 2) Course CRUD
    r = client.post("/courses", json={"id": 10, "level": "101"})
    assert r.status_code == 200
    r = client.get("/courses/10")
    assert r.status_code == 200 and r.json()["level"] == "101"
    # 3) Enrollment CRUD
    r = client.post("/enrollments", json={"student_id": 1, "course_id": 10})
    assert r.status_code == 200
    enrollment = r.json()
    eid = enrollment["id"]
    r = client.get(f"/enrollments/{eid}")
    assert r.status_code == 200 and r.json()["student_id"] == 1
    # 4) Teacher CRUD
    r = client.post("/teachers", json={"id": 900})
    assert r.status_code == 200
    r = client.get("/teachers/900")
    assert r.status_code == 200
    # 5) Teaching CRUD
    r = client.post("/teachings", json={"teacher_id": 900, "course_id": 10})
    assert r.status_code == 200
    t = r.json()
    tid = t["id"]
    r = client.get(f"/teachings/{tid}")
    assert r.status_code == 200 and r.json()["teacher_id"] == 900
    print("SMOKE TEST PASSED")
    return True
if __name__ == "__main__":
    try:
        run_smoke_test()
    except AssertionError as e:
        print("SMOKE TEST FAILED:", e)
        raise SystemExit(1)