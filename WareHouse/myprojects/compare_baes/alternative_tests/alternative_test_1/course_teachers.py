'''
Course-Teacher assignment router: Create and manage assignments between courses and teachers.
'''
'''
Course-Teacher assignment router: Create and manage assignments between courses and teachers.
'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import CourseTeacher, Course, Teacher
import schemas
router = APIRouter()
@router.post("/", response_model=schemas.CourseTeacherRead, status_code=status.HTTP_201_CREATED)
def assign_teacher(payload: schemas.CourseTeacherCreate, db: Session = Depends(get_db)):
    course = db.get(Course, payload.course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    teacher = db.get(Teacher, payload.teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    # uniqueness
    existing = db.query(CourseTeacher).filter_by(course_id=payload.course_id, teacher_id=payload.teacher_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Assignment already exists")
    assignment = CourseTeacher(course_id=payload.course_id, teacher_id=payload.teacher_id)
    db.add(assignment)
    db.flush()
    db.refresh(assignment)
    return assignment
@router.get("/", response_model=List[schemas.CourseTeacherRead])
def list_assignments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(CourseTeacher).offset(skip).limit(limit).all()
@router.get("/{assignment_id}", response_model=schemas.CourseTeacherRead)
def get_assignment(assignment_id: int, db: Session = Depends(get_db)):
    a = db.get(CourseTeacher, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return a
@router.delete("/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    a = db.get(CourseTeacher, assignment_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assignment not found")
    db.delete(a)
    return