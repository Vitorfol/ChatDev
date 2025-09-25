'''
FastAPI router definitions for Students, Courses, Enrollments, Teachers, Teachings and Migrations.
Endpoints are available from app startup; the handlers will raise clear errors if the corresponding
tables/migrations haven't been applied yet. This allows the API surface to remain stable while the
schema evolves in-process (zero-downtime).
Added endpoints:
 - POST /migrate  -> apply migrations up to a requested step (1..6)
 - POST /smoke    -> run the automated smoke test and return results
'''
from fastapi import APIRouter, HTTPException
from typing import List
from pydantic import BaseModel
from domain import entities as de
from services import StudentService, CourseService, EnrollmentService, TeacherService, TeachingService
from migrations import MigrationService, MIGRATIONS
router = APIRouter()
student_service = StudentService()
course_service = CourseService()
enrollment_service = EnrollmentService()
teacher_service = TeacherService()
teaching_service = TeachingService()
migration_service = MigrationService()
MAX_MIGRATION_STEP = max(MIGRATIONS.keys())
# --- Migrate / Smoke payloads
class MigratePayload(BaseModel):
    step: int
# Students
@router.post("/students", response_model=de.StudentOut)
async def create_student(payload: de.StudentIn):
    try:
        row = student_service.create(payload)
        return de.StudentOut(**row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/students/{student_id}", response_model=de.StudentOut)
async def get_student(student_id: int):
    row = student_service.get(student_id)
    if not row:
        raise HTTPException(status_code=404, detail="student not found")
    return de.StudentOut(**row)
@router.get("/students", response_model=List[de.StudentOut])
async def list_students():
    rows = student_service.list()
    return [de.StudentOut(**r) for r in rows]
@router.put("/students/{student_id}", response_model=de.StudentOut)
async def update_student(student_id: int, payload: de.StudentIn):
    row = student_service.update(student_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="student not found or no updatable columns")
    return de.StudentOut(**row)
@router.delete("/students/{student_id}")
async def delete_student(student_id: int):
    ok = student_service.delete(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="student not found")
    return {"deleted": True}
# Courses
@router.post("/courses", response_model=de.CourseOut)
async def create_course(payload: de.CourseIn):
    try:
        row = course_service.create(payload)
        return de.CourseOut(**row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/courses/{course_id}", response_model=de.CourseOut)
async def get_course(course_id: int):
    row = course_service.get(course_id)
    if not row:
        raise HTTPException(status_code=404, detail="course not found")
    return de.CourseOut(**row)
@router.get("/courses", response_model=List[de.CourseOut])
async def list_courses():
    rows = course_service.list()
    return [de.CourseOut(**r) for r in rows]
@router.put("/courses/{course_id}", response_model=de.CourseOut)
async def update_course(course_id: int, payload: de.CourseIn):
    row = course_service.update(course_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="course not found or no updatable columns")
    return de.CourseOut(**row)
@router.delete("/courses/{course_id}")
async def delete_course(course_id: int):
    ok = course_service.delete(course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="course not found")
    return {"deleted": True}
# Enrollments
@router.post("/enrollments", response_model=de.EnrollmentOut)
async def create_enrollment(payload: de.EnrollmentIn):
    try:
        row = enrollment_service.create(payload)
        return de.EnrollmentOut(**row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/enrollments/{enrollment_id}", response_model=de.EnrollmentOut)
async def get_enrollment(enrollment_id: int):
    row = enrollment_service.get(enrollment_id)
    if not row:
        raise HTTPException(status_code=404, detail="enrollment not found")
    return de.EnrollmentOut(**row)
@router.get("/enrollments", response_model=List[de.EnrollmentOut])
async def list_enrollments():
    rows = enrollment_service.list()
    return [de.EnrollmentOut(**r) for r in rows]
@router.put("/enrollments/{enrollment_id}", response_model=de.EnrollmentOut)
async def update_enrollment(enrollment_id: int, payload: de.EnrollmentIn):
    row = enrollment_service.update(enrollment_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="enrollment not found")
    return de.EnrollmentOut(**row)
@router.delete("/enrollments/{enrollment_id}")
async def delete_enrollment(enrollment_id: int):
    ok = enrollment_service.delete(enrollment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="enrollment not found")
    return {"deleted": True}
# Teachers
@router.post("/teachers", response_model=de.TeacherOut)
async def create_teacher(payload: de.TeacherIn):
    try:
        row = teacher_service.create(payload)
        return de.TeacherOut(**row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/teachers/{teacher_id}", response_model=de.TeacherOut)
async def get_teacher(teacher_id: int):
    row = teacher_service.get(teacher_id)
    if not row:
        raise HTTPException(status_code=404, detail="teacher not found")
    return de.TeacherOut(**row)
@router.get("/teachers", response_model=List[de.TeacherOut])
async def list_teachers():
    rows = teacher_service.list()
    return [de.TeacherOut(**r) for r in rows]
@router.delete("/teachers/{teacher_id}")
async def delete_teacher(teacher_id: int):
    ok = teacher_service.delete(teacher_id)
    if not ok:
        raise HTTPException(status_code=404, detail="teacher not found")
    return {"deleted": True}
# Teachings
@router.post("/teachings", response_model=de.TeachingOut)
async def create_teaching(payload: de.TeachingIn):
    try:
        row = teaching_service.create(payload)
        return de.TeachingOut(**row)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/teachings/{teaching_id}", response_model=de.TeachingOut)
async def get_teaching(teaching_id: int):
    row = teaching_service.get(teaching_id)
    if not row:
        raise HTTPException(status_code=404, detail="teaching not found")
    return de.TeachingOut(**row)
@router.get("/teachings", response_model=List[de.TeachingOut])
async def list_teachings():
    rows = teaching_service.list()
    return [de.TeachingOut(**r) for r in rows]
@router.put("/teachings/{teaching_id}", response_model=de.TeachingOut)
async def update_teaching(teaching_id: int, payload: de.TeachingIn):
    row = teaching_service.update(teaching_id, payload)
    if not row:
        raise HTTPException(status_code=404, detail="teaching not found")
    return de.TeachingOut(**row)
@router.delete("/teachings/{teaching_id}")
async def delete_teaching(teaching_id: int):
    ok = teaching_service.delete(teaching_id)
    if not ok:
        raise HTTPException(status_code=404, detail="teaching not found")
    return {"deleted": True}
# Migration introspection
@router.get("/migrations")
async def migrations_list():
    from db import get_applied_steps
    return {"applied_steps": get_applied_steps()}
# In-process migration endpoint
@router.post("/migrate")
async def migrate(payload: MigratePayload):
    step = payload.step
    if not (1 <= step <= MAX_MIGRATION_STEP):
        raise HTTPException(status_code=400, detail=f"step must be between 1 and {MAX_MIGRATION_STEP}")
    try:
        applied = migration_service.apply_up_to(step)
        return {"applied_steps": applied}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Smoke test endpoint
@router.post("/smoke")
async def smoke():
    # Import here to avoid potential circular imports at module import time
    from smoke_test import run_smoke_test
    ok, details = run_smoke_test()
    return {"ok": ok, "details": details}