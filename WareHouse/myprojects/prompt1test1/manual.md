# School Management — User Manual

A small FastAPI + SQLite backend with a Tkinter GUI client for managing Students, Teachers, Courses and enrollments (Student <-> Course, Teacher -> Course).  
This manual explains what the system does, how to install dependencies, how to run it, API reference, GUI usage, troubleshooting and tips for production use.

Contents
- Overview
- Quick prerequisites
- Install & setup
- Initialize the database
- Running the API server (example app)
- Running the GUI client
- API endpoints (reference)
- GUI: main functions & how to use
- Data model & validation rules
- Troubleshooting & tips
- Production notes & suggested enhancements
- Contact / support

Overview
- Features:
  - CRUD endpoints for Students, Teachers and Courses.
  - Student has an email attribute (validated as EmailStr).
  - Course has a level attribute (enum: beginner | intermediate | advanced).
  - Relationships:
    - Many-to-many: Student <-> Course (enrollments).
    - One-to-many: Teacher -> Course (a course may have an optional teacher).
  - A Tkinter GUI (main.py) that consumes the API to create/list/delete entities and manage enrollments.
- Storage: SQLite (file: school.db).
- Provided files (key):
  - database.py — SQLAlchemy engine, session and Base.
  - models.py — SQLAlchemy models for Student, Teacher, Course and enrollments association table.
  - schemas.py — Pydantic schemas & Course Level enum.
  - crud.py — Database operation helpers (create/get/update/delete + enrollment helpers).
  - main.py — Tkinter GUI client (talks to API_URL = "http://127.0.0.1:8000").
  - requirements.txt — Python dependencies.

Quick prerequisites
- Python 3.8+ (3.9/3.10/3.11 recommended)
- pip
- System GUI support for Tkinter (if you want to run the GUI):
  - On Debian/Ubuntu: sudo apt install python3-tk
  - On RHEL/CentOS/Fedora: sudo dnf install python3-tkinter (package name may vary)
  - On Windows / macOS, Tkinter is usually included with the standard Python installer
- If running on a headless server you can still run the API but not the GUI.

Install & setup (local dev)
1. Clone the repository (or ensure the project files are present).
2. Create and activate a virtual environment:
   - Linux/macOS:
     python3 -m venv .venv
     source .venv/bin/activate
   - Windows (PowerShell):
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
3. Install Python dependencies:
   - pip install -r requirements.txt
   Note: tkinter is not installed via pip on many platforms — install the OS package as noted above if the GUI fails to import tkinter.

Initialize the database
- The app uses SQLite at ./school.db. Create tables (one-time) by running a short Python snippet or ensure the FastAPI app creates tables at startup.

Quick one-liner to create tables:
python -c "from database import engine, Base; import models; Base.metadata.create_all(bind=engine); print('DB initialized')"

(That will create school.db in the project folder and create the tables defined in models.py.)

Running the API server
- The repository provides models, schemas and crud helpers, but not necessarily a backed example FastAPI app file. If an API server file (e.g., app.py or api.py) exists in your repo, run it with uvicorn. If not, here's a minimal example you can save as app.py in the project root and run.

Example FastAPI application (save as app.py)

```python
# app.py  (example)
from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import SessionLocal, engine, Base
from sqlalchemy.exc import IntegrityError

# Create DB tables (safe to run multiple times)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="School Management API")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Students
@app.post("/students/", response_model=schemas.StudentRead)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_student(db, student)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.get("/students/", response_model=List[schemas.StudentRead])
def list_students(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_students(db, skip=skip, limit=limit)

@app.get("/students/{student_id}", response_model=schemas.StudentRead)
def get_student(student_id: int, db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return s

@app.put("/students/{student_id}", response_model=schemas.StudentRead)
def update_student(student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    try:
        return crud.update_student(db, s, updates)
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")

@app.delete("/students/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    crud.delete_student(db, s)
    return {"detail": "deleted"}

@app.get("/students/{student_id}/courses", response_model=List[schemas.CourseRead])
def student_courses(student_id: int, db: Session = Depends(get_db)):
    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    return crud.get_courses_for_student(db, s)

# Teachers
@app.post("/teachers/", response_model=schemas.TeacherRead)
def create_teacher(teacher: schemas.TeacherCreate, db: Session = Depends(get_db)):
    return crud.create_teacher(db, teacher)

@app.get("/teachers/", response_model=List[schemas.TeacherRead])
def list_teachers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_teachers(db, skip=skip, limit=limit)

@app.get("/teachers/{teacher_id}", response_model=schemas.TeacherRead)
def get_teacher(teacher_id: int, db: Session = Depends(get_db)):
    t = crud.get_teacher(db, teacher_id)
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return t

@app.delete("/teachers/{teacher_id}")
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    t = crud.get_teacher(db, teacher_id)
    if not t:
        raise HTTPException(status_code=404, detail="Teacher not found")
    crud.delete_teacher(db, t)
    return {"detail": "deleted"}

# Courses
@app.post("/courses/", response_model=schemas.CourseRead)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    # optionally validate teacher exists if teacher_id provided
    if course.teacher_id is not None:
        teacher = crud.get_teacher(db, course.teacher_id)
        if not teacher:
            raise HTTPException(status_code=404, detail="Teacher not found")
    return crud.create_course(db, course)

@app.get("/courses/", response_model=List[schemas.CourseRead])
def list_courses(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_courses(db, skip=skip, limit=limit)

@app.get("/courses/{course_id}", response_model=schemas.CourseRead)
def get_course(course_id: int, db: Session = Depends(get_db)):
    c = crud.get_course(db, course_id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return c

@app.delete("/courses/{course_id}")
def delete_course(course_id: int, db: Session = Depends(get_db)):
    c = crud.get_course(db, course_id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    crud.delete_course(db, c)
    return {"detail": "deleted"}

@app.post("/courses/{course_id}/enroll/{student_id}")
def enroll(course_id: int, student_id: int, db: Session = Depends(get_db)):
    c = crud.get_course(db, course_id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    crud.enroll_student_in_course(db, c, s)
    return {"detail": "enrolled"}

@app.delete("/courses/{course_id}/unenroll/{student_id}")
def unenroll(course_id: int, student_id: int, db: Session = Depends(get_db)):
    c = crud.get_course(db, course_id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    s = crud.get_student(db, student_id)
    if not s:
        raise HTTPException(status_code=404, detail="Student not found")
    crud.unenroll_student_from_course(db, c, s)
    return {"detail": "unenrolled"}

@app.get("/courses/{course_id}/students", response_model=List[schemas.StudentRead])
def students_in_course(course_id: int, db: Session = Depends(get_db)):
    c = crud.get_course(db, course_id)
    if not c:
        raise HTTPException(status_code=404, detail="Course not found")
    return crud.get_students_in_course(db, c)
```

Run the API with uvicorn:
- uvicorn app:app --reload --host 127.0.0.1 --port 8000

By default the GUI expects the API at http://127.0.0.1:8000. If you run API on a different host/port, update API_URL in main.py to match.

Running the GUI client
- Ensure the API server is running.
- Run:
  python main.py
- The GUI uses the constant API_URL in main.py. If your server is remote or using a different port, edit:
  API_URL = "http://127.0.0.1:8000"
  to the correct address.

API Endpoints — Reference
(These match the example app and the GUI expectations)

Students
- GET /students/ — list students (query params skip, limit)
  - Response: list of StudentRead objects
- POST /students/ — create student
  - Body: { "name": "Alice", "email": "alice@example.com" }
  - Response: created StudentRead
- GET /students/{id} — get student
- PUT /students/{id} — update student
  - Body (any subset): { "name": "New Name", "email": "new@example.com" }
- DELETE /students/{id}
- GET /students/{id}/courses — get courses the student is enrolled in (CourseRead objects)

Teachers
- GET /teachers/
- POST /teachers/ — { "name": "Mr. Smith" }
- GET /teachers/{id}
- DELETE /teachers/{id}

Courses
- GET /courses/ — returns CourseRead (includes teacher object and list of students)
- POST /courses/ — create course
  - Body: { "title": "Algebra I", "level": "beginner", "teacher_id": 1 } (teacher_id optional)
  - level must be one of: "beginner", "intermediate", "advanced"
- GET /courses/{id}
- DELETE /courses/{id}
- POST /courses/{course_id}/enroll/{student_id}
- DELETE /courses/{course_id}/unenroll/{student_id}
- GET /courses/{course_id}/students

Example curl
- Create student:
  curl -X POST "http://127.0.0.1:8000/students/" -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'
- Enroll:
  curl -X POST "http://127.0.0.1:8000/courses/1/enroll/1"

GUI: main functions & how to use
- The GUI has 4 tabs: Students, Teachers, Courses, Enrollments.

Students tab
- Create Student: enter Name and Email, click Create (email validated server-side).
- Student list: shows ID, Name, Email. Use Refresh to reload.
- Delete Selected: deletes the selected student.

Teachers tab
- Create Teacher: enter Name and Create.
- List shows ID and name, Refresh, and Delete Selected.

Courses tab
- Create Course: Title, Level (enter textual value; recommended to use one of beginner/intermediate/advanced), Teacher ID (optional — provide an existing teacher ID).
- Course list shows ID, Title, Level, Teacher name.
- Delete Selected: delete selected course.

Enrollments tab
- Enroll / Unenroll: provide Course ID and Student ID and use Enroll or Unenroll.
- View Students in Course: enter course id and click; will list enrolled students with ID, name, email.
- View Courses for Student: enter student id and click; shows course details including teacher.

Notes on GUI usage
- Use Refresh buttons after changes (the GUI does attempt to refresh after creates, but manual refresh is helpful).
- The GUI assumes the API returns teacher as object under course => course["teacher"] is used to display the teacher name.
- If the API returns 404 or other errors, GUI will show a messagebox with server message or text.

Data model & validation
- Student:
  - id: integer (auto)
  - name: string (required)
  - email: EmailStr (required, unique)
- Teacher:
  - id, name (required)
- Course:
  - id, title, level, teacher_id (nullable)
  - level is an enum string: "beginner" | "intermediate" | "advanced"
- Relationships:
  - students <-> courses is many-to-many via enrollments association table.
  - teacher -> courses is one-to-many via teacher_id FK (nullable).

Troubleshooting & common issues
- GUI fails to start: Check Tkinter availability. On Linux install python3-tk.
- GUI says "Could not reach API": Ensure uvicorn API server is running on the API_URL set in main.py and port is correct.
- Database locked errors: SQLite can report "database is locked" in concurrent writes. Workarounds:
  - Avoid running many concurrent write-heavy requests.
  - For production, use PostgreSQL / MySQL.
- Email duplicates: Creating a student with an existing email will raise an integrity error (400).
- Course creation with invalid teacher_id: returns 404 if teacher doesn't exist.
- Headless server: GUI requires an X display. Use the API alone on servers.
- Port conflicts: If uvicorn fails to bind, choose another port and update API_URL in main.py.

Production notes & suggested enhancements
- Authentication & Authorization:
  - Add JWT/OAuth2 for protected API endpoints for production.
- Database:
  - Move from SQLite to PostgreSQL for multi-user or high concurrency.
  - Add migrations via Alembic.
- Validation & constraints:
  - Add more validation (e.g., max lengths).
- Testing:
  - Add unit tests for CRUD and integration tests for endpoints.
- CORS:
  - If the GUI or other frontends are remote, enable CORS in FastAPI (fastapi.middleware.cors.CORSMiddleware).
- Logging & monitoring:
  - Add structured logging and metrics.
- UI:
  - Consider adding a web-based UI (FastAPI + simple frontend) instead of Tkinter for cross-platform/browser use.

FAQ
- Q: The GUI shows empty teacher for courses created without teacher_id — expected.
- Q: How to change DB file location? Edit SQLALCHEMY_DATABASE_URL in database.py.
- Q: How to pre-populate data? Use curl or write a small Python script that uses crud functions to create records.

Appendix — Useful commands
- Initialize DB:
  python -c "from database import engine, Base; import models; Base.metadata.create_all(bind=engine)"
- Start API (example):
  uvicorn app:app --reload --host 127.0.0.1 --port 8000
- Run GUI:
  python main.py

Contact / support
- For issues running the project, provide:
  - Python version
  - OS & whether a virtualenv is used
  - The exact error trace or screenshot of error dialog
- For feature requests: propose desired features (search, pagination, auth, CSV import/export, reporting, etc.)

End of manual

If you want, I can:
- produce a ready-to-run app.py with the exact endpoints wired to your crud.py (I provided an example above which you can save as app.py), or
- create a quick shell script to initialize DB and start both server and GUI, or
- create a short test data seeder to populate the DB with sample students/teachers/courses.