'''
FastAPI router definitions and endpoint wiring.
Routers expose CRUD endpoints for Students, Courses, Enrollments, Teachers,
Teachings, and an endpoint to apply the next migration. Endpoints use services
which handle repository and transaction logic.
'''
from fastapi import APIRouter, HTTPException
from services import (
    StudentService, CourseService, TeacherService,
    EnrollmentService, TeachingService, ServiceError
)
from models import (
    StudentCreate, StudentOut, StudentUpdate,
    CourseCreate, CourseOut, CourseUpdate,
    TeacherCreate, TeacherOut,
    EnrollmentCreate, EnrollmentOut,
    TeachingCreate, TeachingOut
)
from migrations import migration_manager
router = APIRouter()
student_svc = StudentService()
course_svc = CourseService()
teacher_svc = TeacherService()
enrollment_svc = EnrollmentService()
teaching_svc = TeachingService()
# ---------------- Students ----------------
@router.post("/students", response_model=StudentOut)
def create_student(payload: StudentCreate):
    try:
        s = student_svc.create_student(id=payload.id, email=payload.email)
        return s
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/students")
def list_students():
    return student_svc.list_students()
@router.get("/students/{student_id}", response_model=StudentOut)
def get_student(student_id: int):
    s = student_svc.get_student(student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s
@router.put("/students/{student_id}", response_model=StudentOut)
def update_student(student_id: int, payload: StudentUpdate):
    s = student_svc.update_student(student_id, email=payload.email)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s
@router.delete("/students/{student_id}")
def delete_student(student_id: int):
    ok = student_svc.delete_student(student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"deleted": True}
# ---------------- Courses ----------------
@router.post("/courses", response_model=CourseOut)
def create_course(payload: CourseCreate):
    try:
        c = course_svc.create_course(id=payload.id, level=payload.level)
        return c
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/courses")
def list_courses():
    return course_svc.list_courses()
@router.get("/courses/{course_id}", response_model=CourseOut)
def get_course(course_id: int):
    c = course_svc.get_course(course_id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c
@router.put("/courses/{course_id}", response_model=CourseOut)
def update_course(course_id: int, payload: CourseUpdate):
    c = course_svc.update_course(course_id, level=payload.level)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c
@router.delete("/courses/{course_id}")
def delete_course(course_id: int):
    ok = course_svc.delete_course(course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return {"deleted": True}
# ---------------- Enrollments ----------------
@router.post("/enrollments", response_model=EnrollmentOut)
def create_enrollment(payload: EnrollmentCreate):
    try:
        e = enrollment_svc.create_enrollment(student_id=payload.student_id, course_id=payload.course_id)
        return e
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/enrollments")
def list_enrollments():
    return enrollment_svc.list_enrollments()
@router.get("/enrollments/{enrollment_id}", response_model=EnrollmentOut)
def get_enrollment(enrollment_id: int):
    e = enrollment_svc.get_enrollment(enrollment_id)
    if not e:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return e
@router.delete("/enrollments/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    ok = enrollment_svc.delete_enrollment(enrollment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return {"deleted": True}
# ---------------- Teachers ----------------
@router.post("/teachers", response_model=TeacherOut)
def create_teacher(payload: TeacherCreate):
    try:
        t = teacher_svc.create_teacher(id=payload.id)
        return t
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/teachers")
def list_teachers():
    return teacher_svc.list_teachers()
@router.get("/teachers/{teacher_id}", response_model=TeacherOut)
def get_teacher(teacher_id: int):
    t = teacher_svc.get_teacher(teacher_id)
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return t
@router.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int):
    ok = teacher_svc.delete_teacher(teacher_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {"deleted": True}
# ---------------- Teachings ----------------
@router.post("/teachings", response_model=TeachingOut)
def create_teaching(payload: TeachingCreate):
    try:
        t = teaching_svc.create_teaching(teacher_id=payload.teacher_id, course_id=payload.course_id)
        return t
    except ServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/teachings")
def list_teachings():
    return teaching_svc.list_teachings()
@router.get("/teachings/{teaching_id}", response_model=TeachingOut)
def get_teaching(teaching_id: int):
    t = teaching_svc.get_teaching(teaching_id)
    if not t:
        raise HTTPException(status_code=404, detail="Teaching not found")
    return t
@router.delete("/teachings/{teaching_id}")
def delete_teaching(teaching_id: int):
    ok = teaching_svc.delete_teaching(teaching_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Teaching not found")
    return {"deleted": True}
# ---------------- Migrations ----------------
@router.post("/migrations/apply_next")
def apply_next_migration():
    """
    Apply the next migration step. This endpoint enables incremental, zero-downtime
    schema evolution in-process without restarting the server.
    """
    result = migration_manager.apply_next()
    return result
@router.get("/migrations/version")
def get_migration_version():
    return {"version": migration_manager.current_version(), "total_migrations": len(migration_manager.migrations)}