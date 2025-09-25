'''
Enrollments router: Manage many-to-many relationship between Student and Course
via explicit enrollment table. Endpoints to create, list, get and delete enrollments.
'''
'''
Enrollments router: Manage many-to-many relationship between Student and Course
via explicit enrollment table. Endpoints to create, list, get and delete enrollments.
'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import Enrollment, Student, Course
import schemas
router = APIRouter()
@router.post("/", response_model=schemas.EnrollmentRead, status_code=status.HTTP_201_CREATED)
def create_enrollment(payload: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    # check existence
    student = db.get(Student, payload.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    course = db.get(Course, payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    # ensure uniqueness
    existing = db.query(Enrollment).filter_by(student_id=payload.student_id, course_id=payload.course_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Enrollment already exists")
    enr = Enrollment(student_id=payload.student_id, course_id=payload.course_id)
    db.add(enr)
    db.flush()
    db.refresh(enr)
    return enr
@router.get("/", response_model=List[schemas.EnrollmentRead])
def list_enrollments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Enrollment).offset(skip).limit(limit).all()
@router.get("/{enrollment_id}", response_model=schemas.EnrollmentRead)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    enr = db.get(Enrollment, enrollment_id)
    if not enr:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    return enr
@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    enr = db.get(Enrollment, enrollment_id)
    if not enr:
        raise HTTPException(status_code=404, detail="Enrollment not found")
    db.delete(enr)
    return