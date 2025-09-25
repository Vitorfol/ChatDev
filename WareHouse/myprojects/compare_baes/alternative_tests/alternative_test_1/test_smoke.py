'''
Automated smoke/regression tests using FastAPI TestClient.
Performs basic CRUD checks for Student, Course, Enrollment, Teacher, and assignments.
Run with pytest.
'''
'''
Automated smoke/regression tests using FastAPI TestClient.
Performs basic CRUD checks for Student, Course, Enrollment, Teacher, and assignments.
Run with pytest.
'''
from fastapi.testclient import TestClient
import os
from main import app
client = TestClient(app)
def test_smoke_workflow():
    # Create Student
    r = client.post("/students/", json={"name": "Alice", "email": "alice@example.com"})
    assert r.status_code == 201
    student = r.json()
    assert student["name"] == "Alice"
    sid = student["id"]
    # Update Student
    r = client.put(f"/students/{sid}", json={"name": "Alice A."})
    assert r.status_code == 200
    assert r.json()["name"] == "Alice A."
    # Create Course
    r = client.post("/courses/", json={"title": "Intro to Testing", "level": "Beginner"})
    assert r.status_code == 201
    course = r.json()
    cid = course["id"]
    assert course["title"] == "Intro to Testing"
    # Enroll student in course
    r = client.post("/enrollments/", json={"student_id": sid, "course_id": cid})
    assert r.status_code == 201
    enrollment = r.json()
    eid = enrollment["id"]
    # Create Teacher
    r = client.post("/teachers/", json={"name": "Dr. Smith", "department": "Computer Science"})
    assert r.status_code == 201
    teacher = r.json()
    tid = teacher["id"]
    # Assign teacher to course
    r = client.post("/course-teachers/", json={"course_id": cid, "teacher_id": tid})
    assert r.status_code == 201
    assign = r.json()
    assign_id = assign["id"]
    # List checks
    r = client.get("/students/")
    assert r.status_code == 200
    assert any(s["id"] == sid for s in r.json())
    r = client.get("/courses/")
    assert r.status_code == 200
    assert any(c["id"] == cid for c in r.json())
    r = client.get("/teachers/")
    assert r.status_code == 200
    assert any(t["id"] == tid for t in r.json())
    # Delete enrollment
    r = client.delete(f"/enrollments/{eid}")
    assert r.status_code == 204
    # Delete assignment
    r = client.delete(f"/course-teachers/{assign_id}")
    assert r.status_code == 204
    # Delete course and student and teacher (cleanup)
    r = client.delete(f"/courses/{cid}")
    assert r.status_code == 204
    r = client.delete(f"/students/{sid}")
    assert r.status_code == 204
    r = client.delete(f"/teachers/{tid}")
    assert r.status_code == 204