'''
FastAPI application providing CRUD endpoints for Student, Course, and Teacher entities.
Adds email field to Student and level attribute to Course. Implements relationships:
- Student <-> Course (many-to-many)
- Teacher -> Course (one-to-many)
Uses SQLite (via database.py) for persistence and SQLAlchemy ORM for DB operations.
Endpoints implemented (non-exhaustive, but covering GUI needs):
- Students:
  - GET    /students/                 -> list students
  - POST   /students/                 -> create student
  - GET    /students/{student_id}     -> get student
  - PUT    /students/{student_id}     -> update student
  - DELETE /students/{student_id}     -> delete student
  - GET    /students/{student_id}/courses -> list courses for a student
  - POST   /students/{student_id}/enroll/{course_id} -> enroll student in course
  - DELETE /students/{student_id}/unenroll/{course_id} -> unenroll student from course
- Courses:
  - GET    /courses/                  -> list courses
  - POST   /courses/                  -> create course (optional teacher_id)
  - GET    /courses/{course_id}       -> get course (includes students)
  - PUT    /courses/{course_id}       -> update course (title/desc/level/teacher_id)
  - DELETE /courses/{course_id}       -> delete course
  - POST   /courses/{course_id}/assign_teacher/{teacher_id} -> assign teacher to course
- Teachers:
  - GET    /teachers/                 -> list teachers
  - POST   /teachers/                 -> create teacher
  - GET    /teachers/{teacher_id}     -> get teacher
  - PUT    /teachers/{teacher_id}     -> update teacher
  - DELETE /teachers/{teacher_id}     -> delete teacher
  - GET    /teachers/{teacher_id}/courses -> list courses for a teacher
This file depends on the modules: database.py, models.py, schemas.py, crud.py
'''
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
import database
import models
import schemas
import crud
# Create DB tables (if not present)
models.Base.metadata.create_all(bind=database.engine)
app = FastAPI(title="School Management API")
# Dependency to get DB session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
# -------------------------
# Student endpoints
# -------------------------
@app.get("/students/", response_model=List[schemas.StudentRead])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    students = crud.get_students(db, skip=skip, limit=limit)
    return students
@app.post("/students/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    # enforce unique email
    existing = crud.get_student_by_email(db, email=str(student.email))
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_student = crud.create_student(db, student)
    return db_student
@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return db_student
@app.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, student_update: schemas.StudentUpdate, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    # If updating email, ensure uniqueness
    if student_update.email is not None:
        existing = crud.get_student_by_email(db, email=str(student_update.email))
        if existing and existing.id != db_student.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered to another student")
    updated = crud.update_student(db, db_student, student_update)
    return updated
@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    crud.delete_student(db, db_student)
    return None
@app.get("/students/{student_id}/courses", response_model=List[schemas.CourseSimple])
def get_student_courses(student_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    courses = crud.get_courses_for_student(db, db_student)
    return courses
@app.post("/students/{student_id}/enroll/{course_id}")
def enroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    crud.enroll_student_in_course(db, db_student, db_course)
    return {"detail": "Student enrolled"}
@app.delete("/students/{student_id}/unenroll/{course_id}")
def unenroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
    db_student = crud.get_student(db, student_id=student_id)
    if not db_student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    crud.remove_student_from_course(db, db_student, db_course)
    return {"detail": "Student unenrolled"}
# -------------------------
# Course endpoints
# -------------------------
@app.get("/courses/", response_model=List[schemas.CourseRead])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    courses = crud.get_courses(db, skip=skip, limit=limit)
    return courses
@app.post("/courses/", response_model=schemas.CourseRead, status_code=status.HTTP_201_CREATED)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    try:
        db_course = crud.create_course(db, course)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return db_course
@app.get("/courses/{course_id}", response_model=schemas.CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return db_course
@app.put("/courses/{course_id}", response_model=schemas.CourseRead)
def update_course(course_id: int, course_update: schemas.CourseUpdate, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    try:
        updated = crud.update_course(db, db_course, course_update)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return updated
@app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    crud.delete_course(db, db_course)
    return None
@app.post("/courses/{course_id}/assign_teacher/{teacher_id}")
def assign_teacher(course_id: int, teacher_id: int, db: Session = Depends(get_db)):
    db_course = crud.get_course(db, course_id=course_id)
    if not db_course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    db_teacher = crud.get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    updated = crud.assign_teacher_to_course(db, db_course, db_teacher)
    return {"detail": "Teacher assigned", "course_id": updated.id}
# -------------------------
# Teacher endpoints
# -------------------------
@app.get("/teachers/", response_model=List[schemas.TeacherRead])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teachers = crud.get_teachers(db, skip=skip, limit=limit)
    return teachers
@app.post("/teachers/", response_model=schemas.TeacherRead, status_code=status.HTTP_201_CREATED)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    # if email provided, ensure uniqueness
    if teacher.email is not None:
        existing = crud.get_teacher_by_email(db, email=str(teacher.email))
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    db_teacher = crud.create_teacher(db, teacher)
    return db_teacher
@app.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = crud.get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    return db_teacher
@app.put("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def update_teacher(teacher_id: int, teacher_update: schemas.TeacherUpdate, db: Session = Depends(get_db)):
    db_teacher = crud.get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    # if changing email, ensure uniqueness
    if teacher_update.email is not None:
        existing = crud.get_teacher_by_email(db, email=str(teacher_update.email))
        if existing and existing.id != db_teacher.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered to another teacher")
    updated = crud.update_teacher(db, db_teacher, teacher_update)
    return updated
@app.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = crud.get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    crud.delete_teacher(db, db_teacher)
    return None
@app.get("/teachers/{teacher_id}/courses", response_model=List[schemas.CourseSimple])
def get_teacher_courses(teacher_id: int, db: Session = Depends(get_db)):
    db_teacher = crud.get_teacher(db, teacher_id=teacher_id)
    if not db_teacher:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Teacher not found")
    courses = crud.get_courses_for_teacher(db, db_teacher)
    return courses