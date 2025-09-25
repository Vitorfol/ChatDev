'''
FastAPI API router exposing endpoints for students, courses, teachers, enrollments, and teachings.
Uses the service layer to perform operations.
'''
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from db import get_db
from sqlalchemy.orm import Session
import schemas
import services
router = APIRouter()
# --- Student endpoints ---
@router.post("/students", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student_in: schemas.StudentCreate, db: Session = Depends(get_db)):
    svc = services.StudentService(db)
    try:
        student = svc.create_student(student_in)
        return student
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.get("/students", response_model=List[schemas.StudentOut])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    svc = services.StudentService(db)
    return svc.list_students(skip=skip, limit=limit)
@router.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    svc = services.StudentService(db)
    try:
        return svc.get_student(student_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Student not found")
@router.put("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    svc = services.StudentService(db)
    try:
        return svc.update_student(student_id, updates)
    except LookupError:
        raise HTTPException(status_code=404, detail="Student not found")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    svc = services.StudentService(db)
    try:
        svc.delete_student(student_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Student not found")
    return {}
# --- Course endpoints ---
@router.post("/courses", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    svc = services.CourseService(db)
    return svc.create_course(course_in)
@router.get("/courses", response_model=List[schemas.CourseOut])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    svc = services.CourseService(db)
    return svc.list_courses(skip=skip, limit=limit)
@router.get("/courses/{course_id}", response_model=schemas.CourseOut)
def get_course(course_id: int, db: Session = Depends(get_db)):
    svc = services.CourseService(db)
    try:
        return svc.get_course(course_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Course not found")
@router.put("/courses/{course_id}", response_model=schemas.CourseOut)
def update_course(course_id: int, updates: schemas.CourseUpdate, db: Session = Depends(get_db)):
    svc = services.CourseService(db)
    try:
        return svc.update_course(course_id, updates)
    except LookupError:
        raise HTTPException(status_code=404, detail="Course not found")
@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    svc = services.CourseService(db)
    try:
        svc.delete_course(course_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Course not found")
    return {}
# --- Teacher endpoints ---
@router.post("/teachers", response_model=schemas.TeacherOut, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher_in: schemas.TeacherCreate, db: Session = Depends(get_db)):
    svc = services.TeacherService(db)
    return svc.create_teacher(teacher_in)
@router.get("/teachers", response_model=List[schemas.TeacherOut])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    svc = services.TeacherService(db)
    return svc.list_teachers(skip=skip, limit=limit)
@router.get("/teachers/{teacher_id}", response_model=schemas.TeacherOut)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    svc = services.TeacherService(db)
    try:
        return svc.get_teacher(teacher_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Teacher not found")
@router.put("/teachers/{teacher_id}", response_model=schemas.TeacherOut)
def update_teacher(teacher_id: int, updates: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    svc = services.TeacherService(db)
    try:
        return svc.update_teacher(teacher_id, updates)
    except LookupError:
        raise HTTPException(status_code=404, detail="Teacher not found")
@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    svc = services.TeacherService(db)
    try:
        svc.delete_teacher(teacher_id)
    except LookupError:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return {}
# --- Enrollment endpoints ---
@router.get("/enrollments", response_model=List[schemas.EnrollmentOut])
def list_enrollments(db: Session = Depends(get_db)):
    svc = services.EnrollmentService(db)
    return svc.list_enrollments()
@router.post("/enrollments", status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment_in: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    svc = services.EnrollmentService(db)
    try:
        svc.enroll(enrollment_in.student_id, enrollment_in.course_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "Enrolled"}
@router.delete("/enrollments", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_in: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    svc = services.EnrollmentService(db)
    svc.unenroll(enrollment_in.student_id, enrollment_in.course_id)
    return {}
# --- Teaching endpoints ---
@router.get("/teachings", response_model=List[schemas.TeachingOut])
def list_teachings(db: Session = Depends(get_db)):
    svc = services.TeachingService(db)
    return svc.list_teachings()
@router.post("/teachings", status_code=status.HTTP_201_CREATED)
def create_teaching(teaching_in: schemas.TeachingCreate, db: Session = Depends(get_db)):
    svc = services.TeachingService(db)
    try:
        svc.assign(teaching_in.teacher_id, teaching_in.course_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"detail": "Assigned"}
@router.delete("/teachings", status_code=status.HTTP_204_NO_CONTENT)
def delete_teaching(teaching_in: schemas.TeachingCreate, db: Session = Depends(get_db)):
    svc = services.TeachingService(db)
    svc.unassign(teaching_in.teacher_id, teaching_in.course_id)
    return {}