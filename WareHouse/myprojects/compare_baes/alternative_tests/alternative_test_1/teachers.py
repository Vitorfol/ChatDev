'''
Teachers router: CRUD endpoints for Teacher entity.
'''
'''
Teachers router: CRUD endpoints for Teacher entity.
'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from db import get_db
from models import Teacher
import schemas
router = APIRouter()
@router.post("/", response_model=schemas.TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(payload: schemas.TeacherCreate, db: Session = Depends(get_db)):
    teacher = Teacher(name=payload.name, department=payload.department)
    db.add(teacher)
    db.flush()
    db.refresh(teacher)
    return teacher
@router.get("/", response_model=List[schemas.TeacherRead])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Teacher).offset(skip).limit(limit).all()
@router.get("/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher
@router.put("/{teacher_id}", response_model=schemas.TeacherRead)
def update_teacher(teacher_id: int, payload: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    if payload.name is not None:
        teacher.name = payload.name
    if payload.department is not None:
        teacher.department = payload.department
    db.add(teacher)
    db.flush()
    db.refresh(teacher)
    return teacher
@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.get(Teacher, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    db.delete(teacher)
    return