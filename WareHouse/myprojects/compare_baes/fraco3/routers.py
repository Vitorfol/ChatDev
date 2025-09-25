'''
FastAPI routers for the API endpoints covering Students, Courses, and Teachers.
Provides CRUD endpoints, plus endpoints for enrolling/unenrolling students
and listing students in a course.
'''
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import models
import schemas
import crud
from database import SessionLocal
router = APIRouter()
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# ----------------------------
# Student endpoints
# ----------------------------
@router.post("/students/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student_in: schemas.StudentCreate, db: Session = Depends(get_db)):
    try:
        student = crud.create_student(db, student_in)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create student: {e}")
    return student
@router.get("/students/", response_model=List[schemas.StudentRead])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students
@router.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
@router.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    try:
        student = crud.update_student(db, student_id, updates)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not update student: {e}")
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
@router.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_student(db, student_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student not found")
    return None
@router.post("/students/{student_id}/enroll/{course_id}", status_code=status.HTTP_200_OK)
def enroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
    ok = crud.enroll_student_in_course(db, student_id, course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    return {"detail": "Enrolled successfully"}
@router.delete("/students/{student_id}/unenroll/{course_id}", status_code=status.HTTP_200_OK)
def unenroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
    ok = crud.unenroll_student_from_course(db, student_id, course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Student or Course not found")
    return {"detail": "Unenrolled successfully"}
# ----------------------------
# Teacher endpoints
# ----------------------------
@router.post("/teachers/", response_model=schemas.TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher_in: schemas.TeacherCreate, db: Session = Depends(get_db)):
    teacher = crud.create_teacher(db, teacher_in)
    return teacher
@router.get("/teachers/", response_model=List[schemas.TeacherRead])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = crud.get_teachers(db, skip=skip, limit=limit)
    return teachers
@router.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    teacher = crud.get_teacher(db, teacher_id)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher
@router.put("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def update_teacher(teacher_id: int, updates: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    teacher = crud.update_teacher(db, teacher_id, updates)
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher
@router.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_teacher(db, teacher_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return None
# ----------------------------
# Course endpoints
# ----------------------------
@router.post("/courses/", response_model=schemas.CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(course_in: schemas.CourseCreate, db: Session = Depends(get_db)):
    course = crud.create_course(db, course_in)
    if not course:
        raise HTTPException(status_code=400, detail="Invalid teacher_id provided")
    return course
@router.get("/courses/", response_model=List[schemas.CourseRead])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses
@router.get("/courses/{course_id}", response_model=schemas.CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    course = crud.get_course(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course
@router.put("/courses/{course_id}", response_model=schemas.CourseRead)
def update_course(course_id: int, updates: schemas.CourseUpdate, db: Session = Depends(get_db)):
    course = crud.update_course(db, course_id, updates)
    if course is None:
        raise HTTPException(status_code=400, detail="Invalid teacher_id provided or course not found")
    return course
@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    ok = crud.delete_course(db, course_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Course not found")
    return None
@router.get("/courses/{course_id}/students", response_model=List[schemas.StudentInCourse])
def list_students_in_course(course_id: int, db: Session = Depends(get_db)):
    students = crud.get_students_in_course(db, course_id)
    if students is None:
        raise HTTPException(status_code=404, detail="Course not found")
    return students