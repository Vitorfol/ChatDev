'''
FastAPI routers for Students, Courses, Enrollments, Teachers, Teachings, and migration control.
Routers for Course/Enrollment/Teacher/Teaching are defined and can be mounted at runtime by
MigrationManager to simulate zero-downtime incremental API growth.
'''
from fastapi import APIRouter, HTTPException, status
from typing import List
import services as svc
import schemas
students_router = APIRouter(prefix="/students", tags=["students"])
@students_router.post("", status_code=status.HTTP_201_CREATED)
def create_student(payload: schemas.StudentCreate):
    try:
        svc.create_student(id=payload.id, email=payload.email)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": payload.id, "email": payload.email}
@students_router.get("", response_model=List[schemas.StudentOut])
def list_students():
    try:
        return svc.list_students()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@students_router.get("/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int):
    try:
        student = svc.get_student(student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@students_router.put("/{student_id}")
def update_student(student_id: int, payload: schemas.StudentUpdate):
    try:
        ok = svc.update_student(student_id, payload.email)
        if not ok:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"id": student_id, "email": payload.email}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@students_router.delete("/{student_id}")
def delete_student(student_id: int):
    try:
        ok = svc.delete_student(student_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"deleted": student_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Course router (mounted at migration step 3)
courses_router = APIRouter(prefix="/courses", tags=["courses"])
@courses_router.post("", status_code=status.HTTP_201_CREATED)
def create_course(payload: schemas.CourseCreate):
    try:
        svc.create_course(id=payload.id, level=payload.level)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": payload.id, "level": payload.level}
@courses_router.get("", response_model=List[schemas.CourseOut])
def list_courses():
    try:
        return svc.list_courses()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@courses_router.get("/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int):
    try:
        course = svc.get_course(course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@courses_router.put("/{course_id}")
def update_course(course_id: int, payload: schemas.CourseUpdate):
    try:
        ok = svc.update_course(course_id, payload.level)
        if not ok:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"id": course_id, "level": payload.level}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@courses_router.delete("/{course_id}")
def delete_course(course_id: int):
    try:
        ok = svc.delete_course(course_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Course not found")
        return {"deleted": course_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Enrollment router (mounted at migration step 4)
enrollments_router = APIRouter(prefix="/enrollments", tags=["enrollments"])
@enrollments_router.post("", status_code=status.HTTP_201_CREATED)
def create_enrollment(payload: schemas.EnrollmentCreate):
    try:
        eid = svc.create_enrollment(student_id=payload.student_id, course_id=payload.course_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": eid, "student_id": payload.student_id, "course_id": payload.course_id}
@enrollments_router.get("", response_model=List[schemas.EnrollmentOut])
def list_enrollments():
    try:
        return svc.list_enrollments()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@enrollments_router.get("/{enrollment_id}", response_model=schemas.EnrollmentOut)
def get_enrollment(enrollment_id: int):
    try:
        e = svc.get_enrollment(enrollment_id)
        if not e:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        return e
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@enrollments_router.delete("/{enrollment_id}")
def delete_enrollment(enrollment_id: int):
    try:
        ok = svc.delete_enrollment(enrollment_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Enrollment not found")
        return {"deleted": enrollment_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Teacher router (mounted at migration step 5)
teachers_router = APIRouter(prefix="/teachers", tags=["teachers"])
@teachers_router.post("", status_code=status.HTTP_201_CREATED)
def create_teacher(payload: schemas.TeacherCreate):
    try:
        svc.create_teacher(id=payload.id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": payload.id}
@teachers_router.get("", response_model=list)
def list_teachers():
    try:
        return svc.list_teachers()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@teachers_router.get("/{teacher_id}")
def get_teacher(teacher_id: int):
    try:
        t = svc.get_teacher(teacher_id)
        if not t:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return t
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@teachers_router.delete("/{teacher_id}")
def delete_teacher(teacher_id: int):
    try:
        ok = svc.delete_teacher(teacher_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return {"deleted": teacher_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Teaching router (mounted at migration step 6)
teachings_router = APIRouter(prefix="/teachings", tags=["teachings"])
@teachings_router.post("", status_code=status.HTTP_201_CREATED)
def create_teaching(payload: schemas.TeachingCreate):
    try:
        tid = svc.create_teaching(teacher_id=payload.teacher_id, course_id=payload.course_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"id": tid, "teacher_id": payload.teacher_id, "course_id": payload.course_id}
@teachings_router.get("", response_model=List[schemas.TeachingOut])
def list_teachings():
    try:
        return svc.list_teachings()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@teachings_router.get("/{teaching_id}", response_model=schemas.TeachingOut)
def get_teaching(teaching_id: int):
    try:
        t = svc.get_teaching(teaching_id)
        if not t:
            raise HTTPException(status_code=404, detail="Teaching not found")
        return t
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@teachings_router.delete("/{teaching_id}")
def delete_teaching(teaching_id: int):
    try:
        ok = svc.delete_teaching(teaching_id)
        if not ok:
            raise HTTPException(status_code=404, detail="Teaching not found")
        return {"deleted": teaching_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
# Migration control router
migration_router = APIRouter()
@migration_router.post("/next")
def apply_next_migration():
    """
    Apply the next schema migration (if any). Invoked by tests or clients to evolve the running system.
    """
    # The MigrationManager instance is attached to the FastAPI app during startup in main.py as `migration_manager`.
    import fastapi
    app = fastapi.FastAPI()  # not used; retrieve from context
    # We actually access the global migration manager stored on the application instance.
    from fastapi import Request
    # Use the request scope to get the app - but here we can't access Request. Instead, we will
    # import the MigrationManager via main module (the main process should have created it).
    try:
        from main import migration_manager
    except Exception as e:
        raise HTTPException(status_code=500, detail="Migration manager not available: " + str(e))
    try:
        result = migration_manager.apply_next_migration()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))