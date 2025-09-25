'''
FastAPI server providing CRUD endpoints for Students, Courses, and Teachers.
Features:
- SQLite persistence via SQLAlchemy (database.py).
- Pydantic schemas for validation (schemas.py).
- CRUD operations implemented in crud.py.
- Relationships:
    * Student <-> Course : many-to-many (enroll/remove)
    * Teacher  -> Course : one-to-many (teacher assigned to course)
- Startup creates DB tables automatically.
- Endpoints used by the Tkinter GUI client (examples):
    POST   /students/
    GET    /students/
    POST   /students/{student_id}/courses/{course_id}
    DELETE /students/{student_id}/courses/{course_id}
    POST   /courses/
    GET    /courses/
    POST   /teachers/
    GET    /teachers/
Run with: uvicorn main:app --reload
'''
try:
    # Try to import required runtime modules. If any are missing, we handle that below
    # to provide a helpful error page instead of letting the process crash with
    # ModuleNotFoundError during module import time.
    from fastapi import FastAPI, Depends, HTTPException, status
    from sqlalchemy.orm import Session
    import crud
    import schemas
    from database import get_db, init_db
except Exception as _import_exc:
    # If any import fails (for example sqlalchemy not installed), create a minimal FastAPI
    # application that returns a clear error message explaining what to do.
    missing_detail = str(_import_exc)
    try:
        # Try to extract module name from the ImportError message if possible
        if isinstance(_import_exc, ModuleNotFoundError) and _import_exc.name:
            missing_module = _import_exc.name
        else:
            # Fallback: parse message content
            missing_module = missing_detail.split("'")[1] if "'" in missing_detail else missing_detail
    except Exception:
        missing_module = missing_detail
    from fastapi import FastAPI
    app = FastAPI(title="Education Manager API (dependencies missing)")
    @app.get("/", status_code=200)
    def root():
        """
        Informative endpoint when required dependencies are missing.
        This allows the server process to start and provides instructions
        instead of crashing with ModuleNotFoundError at import-time.
        """
        return {
            "error": "Missing or broken dependency",
            "missing_module": missing_module,
            "message": "Required Python package(s) are not installed. Please run: pip install -r requirements.txt",
            "note": "If you are using a virtual environment, activate it before installing requirements."
        }
    @app.get("/__health__", status_code=200)
    def health_check():
        return {"status": "degraded", "detail": "Application started but required dependencies are missing."}
else:
    app = FastAPI(title="Education Manager API")
    @app.on_event("startup")
    def on_startup():
        """
        Initialize the database (create tables) on application startup.
        """
        init_db()
    # Students endpoints
    @app.post("/students/", response_model=schemas.StudentRead, status_code=status.HTTP_201_CREATED)
    def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
        """
        Create a new student. Email must be unique.
        """
        # Check for existing email
        existing = crud.get_student_by_email(db, student.email)
        if existing:
            raise HTTPException(status_code=400, detail="Student with this email already exists")
        try:
            db_student = crud.create_student(db, student)
            return db_student
        except Exception as e:
            # Generic catch to wrap DB errors
            raise HTTPException(status_code=500, detail=str(e))
    @app.get("/students/", response_model=list[schemas.StudentRead])
    def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        """
        List students with optional pagination.
        """
        students = crud.get_students(db, skip=skip, limit=limit)
        return students
    @app.get("/students/{student_id}", response_model=schemas.StudentRead)
    def get_student(student_id: int, db: Session = Depends(get_db)):
        """
        Retrieve a single student by ID.
        """
        db_student = crud.get_student(db, student_id)
        if not db_student:
            raise HTTPException(status_code=404, detail="Student not found")
        return db_student
    @app.put("/students/{student_id}", response_model=schemas.StudentRead)
    def update_student(student_id: int, student: schemas.StudentUpdate, db: Session = Depends(get_db)):
        """
        Update an existing student. Email uniqueness enforced.
        Uses exclude_unset to ensure only provided fields are applied.
        """
        db_student = crud.get_student(db, student_id)
        if not db_student:
            raise HTTPException(status_code=404, detail="Student not found")
        # Only check email uniqueness if the client provided an email field
        update_data = student.dict(exclude_unset=True)
        if "email" in update_data and update_data["email"] is not None:
            other = crud.get_student_by_email(db, update_data["email"])
            if other and other.id != student_id:
                raise HTTPException(status_code=400, detail="Another student with this email exists")
        try:
            updated = crud.update_student(db, student_id, student)
            return updated
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_student(student_id: int, db: Session = Depends(get_db)):
        """
        Delete a student by ID.
        """
        db_student = crud.get_student(db, student_id)
        if not db_student:
            raise HTTPException(status_code=404, detail="Student not found")
        crud.delete_student(db, student_id)
        return {}
    @app.post("/students/{student_id}/courses/{course_id}", response_model=schemas.StudentRead)
    def enroll_student(student_id: int, course_id: int, db: Session = Depends(get_db)):
        """
        Enroll a student in a course.
        """
        student = crud.get_student(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        course = crud.get_course(db, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        try:
            student = crud.enroll_student(db, student_id, course_id)
            return student
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @app.delete("/students/{student_id}/courses/{course_id}", response_model=schemas.StudentRead)
    def remove_enrollment(student_id: int, course_id: int, db: Session = Depends(get_db)):
        """
        Remove a student's enrollment from a course.
        """
        student = crud.get_student(db, student_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        course = crud.get_course(db, course_id)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        try:
            student = crud.remove_student_from_course(db, student_id, course_id)
            return student
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    # Courses endpoints
    @app.post("/courses/", response_model=schemas.CourseRead, status_code=status.HTTP_201_CREATED)
    def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
        """
        Create a new course. Optionally link to an existing teacher via teacher_id.
        """
        if course.teacher_id is not None:
            teacher = crud.get_teacher(db, course.teacher_id)
            if not teacher:
                raise HTTPException(status_code=404, detail="Teacher not found")
        try:
            db_course = crud.create_course(db, course)
            return db_course
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @app.get("/courses/", response_model=list[schemas.CourseRead])
    def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        """
        List courses with optional pagination.
        """
        courses = crud.get_courses(db, skip=skip, limit=limit)
        return courses
    @app.get("/courses/{course_id}", response_model=schemas.CourseRead)
    def get_course(course_id: int, db: Session = Depends(get_db)):
        """
        Retrieve a single course by ID.
        """
        db_course = crud.get_course(db, course_id)
        if not db_course:
            raise HTTPException(status_code=404, detail="Course not found")
        return db_course
    @app.put("/courses/{course_id}", response_model=schemas.CourseRead)
    def update_course(course_id: int, course: schemas.CourseUpdate, db: Session = Depends(get_db)):
        """
        Update a course's fields.
        Uses exclude_unset to only update fields provided by the client. This avoids
        unintentionally unassigning the teacher when teacher_id is omitted.
        """
        db_course = crud.get_course(db, course_id)
        if not db_course:
            raise HTTPException(status_code=404, detail="Course not found")
        # Validate teacher existence only if teacher_id was included in the request
        update_data = course.dict(exclude_unset=True)
        if "teacher_id" in update_data and update_data["teacher_id"] is not None:
            teacher = crud.get_teacher(db, update_data["teacher_id"])
            if not teacher:
                raise HTTPException(status_code=404, detail="Teacher not found")
        try:
            updated = crud.update_course(db, course_id, course)
            return updated
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @app.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_course(course_id: int, db: Session = Depends(get_db)):
        """
        Delete a course by ID.
        """
        db_course = crud.get_course(db, course_id)
        if not db_course:
            raise HTTPException(status_code=404, detail="Course not found")
        crud.delete_course(db, course_id)
        return {}
    # Teachers endpoints
    @app.post("/teachers/", response_model=schemas.TeacherRead, status_code=status.HTTP_201_CREATED)
    def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
        """
        Create a new teacher.
        """
        try:
            db_teacher = crud.create_teacher(db, teacher)
            return db_teacher
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @app.get("/teachers/", response_model=list[schemas.TeacherRead])
    def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
        """
        List teachers with optional pagination.
        """
        teachers = crud.get_teachers(db, skip=skip, limit=limit)
        return teachers
    @app.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
    def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
        """
        Retrieve a single teacher by ID.
        """
        db_teacher = crud.get_teacher(db, teacher_id)
        if not db_teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        return db_teacher
    @app.put("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
    def update_teacher(teacher_id: int, teacher: schemas.TeacherUpdate, db: Session = Depends(get_db)):
        """
        Update a teacher's details.
        Uses exclude_unset in the CRUD layer to only apply provided fields.
        """
        db_teacher = crud.get_teacher(db, teacher_id)
        if not db_teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        try:
            updated = crud.update_teacher(db, teacher_id, teacher)
            return updated
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    @app.delete("/teachers/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
        """
        Delete a teacher. Associated courses will have teacher_id set to null before deletion.
        """
        db_teacher = crud.get_teacher(db, teacher_id)
        if not db_teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
        crud.delete_teacher(db, teacher_id)
        return {}