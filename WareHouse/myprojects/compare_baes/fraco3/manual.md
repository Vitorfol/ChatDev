# School API + GUI — User Manual

A small Python application that provides:
- A FastAPI-based REST API (SQLite persistence) for managing Students, Courses and Teachers.
- A simple Tkinter GUI client that talks to the API for common tasks (create/list entities, enroll/unenroll students).

This document describes the features, how to install and run the system, the available endpoints, example requests, troubleshooting and basic extension tips.

Contents
- Overview
- Features / main functions
- Project layout (files)
- Installation (dependencies + virtualenv)
- Prepare and run the server (FastAPI)
- Run the GUI client
- API endpoints (paths, methods, payloads, responses & examples)
- Data model / schemas
- Database & reset
- Troubleshooting
- Development notes and extensions

Overview
--------
This system implements a small school-management backend using FastAPI + SQLAlchemy with SQLite storage, and a desktop Tkinter GUI client that interacts with the API.

Main features
-------------
- CRUD for Student, Course and Teacher.
- Student has an email (EmailStr validated).
- Course has a numeric level attribute.
- Relationship: many-to-many between Students and Courses (students can enroll in many courses).
- Relationship: one-to-many Teacher -> Courses (each Course can have one Teacher).
- Endpoints to enroll and unenroll students from courses, and listing students in a course.
- Simple GUI client to create/list entities and to enroll/unenroll.

Project layout
--------------
(Important files included with the project)
- database.py — SQLAlchemy engine, SessionLocal, Base.
- models.py — SQLAlchemy models: Student, Course, Teacher; association table.
- schemas.py — Pydantic schemas for request/response models.
- crud.py — Database access functions used by the API.
- routers.py — APIRouter with all the endpoints (students, courses, teachers).
- main.py — Provided script in this repo is a Tkinter GUI client (note name; see Running below).
- gui_client.py (mentioned in README) — optional; if using a different name for the GUI, adjust commands.
- readme.md — quick run instructions (may contain slight name mismatches).
- school.db — the SQLite database created at runtime (./school.db).

Important note about filenames
- In the supplied code the FastAPI router is defined in routers.py but an app entrypoint file for the API server is not included. To run the API you will create a small server file (example provided below). The provided main.py appears to be the GUI client — so don't use it to start the API server.

Installation
------------
1. Create a Python virtual environment (recommended):
   - Linux / macOS:
     python3 -m venv venv
     source venv/bin/activate
   - Windows (PowerShell):
     python -m venv venv
     .\venv\Scripts\Activate.ps1

2. Install required packages:
   pip install fastapi uvicorn sqlalchemy pydantic requests email-validator

   Explanation:
   - fastapi: web framework
   - uvicorn: ASGI server
   - sqlalchemy: ORM
   - pydantic & email-validator: request validation (EmailStr requires email-validator)
   - requests: used by the Tkinter GUI client

Create a server entrypoint (one-time)
------------------------------------
If you don't have a FastAPI app entrypoint file, create server.py (or app.py) in the project root with this content:

```python
# server.py
from fastapi import FastAPI
from routers import router
from database import engine, Base

def create_app():
    # Create DB tables if not present
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="School API")
    app.include_router(router, prefix="/api")
    return app

app = create_app()

if __name__ == "__main__":
    # Optional: run with python server.py for development (uvicorn recommended)
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
```

This makes sure the API endpoints are available under the /api prefix. The call Base.metadata.create_all(...) will create SQLite tables on first run.

Run server (FastAPI)
--------------------
Preferred (development with auto-reload):
uvicorn server:app --reload --port 8000

(If your server entrypoint filename is app.py, replace server with app.)

Alternative (run server.py directly if using the __main__ block shown above):
python server.py

Open API docs in your browser:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

Run GUI client (Tkinter)
------------------------
The repo provides a GUI client (main.py). This GUI should be launched in a separate terminal after the API server is running.

Run:
python main.py

Important:
- The GUI is configured to use API_BASE = "http://127.0.0.1:8000/api" inside main.py. If you change port or prefix, update this constant accordingly.

What you can do from the GUI:
- Students tab: create student (name + email), list students (shows enrolled courses).
- Courses tab: create course (title, integer level, optional teacher_id), list courses (shows teacher and students).
- Teachers tab: create teacher, list teachers.
- Enrollments tab: enroll or unenroll a student to/from a course using IDs.

API endpoints
-------------
All endpoints are mounted under /api (given server includes router with prefix="/api").

Students
- POST /api/students/
  - Create student
  - Payload: { "name": "Alice", "email": "alice@example.com" }
  - Success: 201 Created — Student object (id, name, email, courses)

- GET /api/students/
  - List students, supports skip & limit query params.
  - Response: list of StudentRead objects

- GET /api/students/{student_id}
  - Get single student

- PUT /api/students/{student_id}
  - Update student (partial)
  - Payload example: { "name": "New Name" } or { "email": "new@example.com" }

- DELETE /api/students/{student_id}
  - Delete student (204 No Content)

- POST /api/students/{student_id}/enroll/{course_id}
  - Enroll a student in a course (200).
  - Response: { "detail": "Enrolled successfully" }

- DELETE /api/students/{student_id}/unenroll/{course_id}
  - Unenroll student from course (200).
  - Response: { "detail": "Unenrolled successfully" }

Courses
- POST /api/courses/
  - Create course
  - Payload: { "title": "Math 101", "level": 100, "teacher_id": 1 } (teacher_id optional)
  - Success: 201 Created — CourseRead includes teacher and students

- GET /api/courses/
  - List courses

- GET /api/courses/{course_id}
  - Get single course

- PUT /api/courses/{course_id}
  - Update course (title, level, teacher_id)
  - Note: If teacher_id is provided, it must be a valid teacher id.

- DELETE /api/courses/{course_id}
  - Delete course

- GET /api/courses/{course_id}/students
  - List students enrolled in a course

Teachers
- POST /api/teachers/
  - Create teacher
  - Payload: { "name": "Prof. Smith" }
  - Response: TeacherRead

- GET /api/teachers/
  - List teachers

- GET /api/teachers/{teacher_id}
  - Get single teacher

- PUT /api/teachers/{teacher_id}
  - Update teacher (e.g., { "name": "New Name" })

- DELETE /api/teachers/{teacher_id}
  - Delete teacher (204)

Example curl requests
---------------------
Create a teacher:
curl -X POST "http://127.0.0.1:8000/api/teachers/" -H "Content-Type: application/json" -d '{"name":"Dr. Jones"}'

Create a course:
curl -X POST "http://127.0.0.1:8000/api/courses/" -H "Content-Type: application/json" -d '{"title":"Physics I","level":101,"teacher_id":1}'

Create a student:
curl -X POST "http://127.0.0.1:8000/api/students/" -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'

Enroll student:
curl -X POST "http://127.0.0.1:8000/api/students/1/enroll/1"

List students in a course:
curl "http://127.0.0.1:8000/api/courses/1/students"

Data model (fields & relationships)
-----------------------------------
Student (models.Student)
- id: integer
- name: string
- email: string (unique, validated as email via Pydantic)
- courses: many-to-many relationship with Course

Course (models.Course)
- id: integer
- title: string
- level: integer (added requirement)
- teacher_id: optional integer FK to Teacher
- teacher: relationship to Teacher
- students: many-to-many with Student

Teacher (models.Teacher)
- id: integer
- name: string
- courses: relationship (one teacher -> many courses)

Pydantic schemas
- StudentCreate / StudentRead (StudentRead includes courses list)
- CourseCreate / CourseRead (CourseRead includes teacher and students)
- TeacherCreate / TeacherRead

Database & persistence
----------------------
- The app uses SQLite file school.db in the project root: SQLALCHEMY_DATABASE_URL = "sqlite:///./school.db"
- Tables are created via Base.metadata.create_all(bind=engine) (see the suggested server.py).
- To reset the database: stop the server and delete school.db, and then restart the server to recreate empty tables:
  rm school.db
  (or delete file via OS file explorer)

Concurrency note:
- database.py sets connect_args={"check_same_thread": False} to allow connections from multiple threads (useful when uvicorn or threads are used).

Common errors & troubleshooting
-------------------------------
- Duplicate email on creating student:
  - You will get a 400 (IntegrityError) because Student.email is unique.
  - Fix by using a different email.

- Invalid teacher_id when creating/updating a Course:
  - The API returns 400 with detail "Invalid teacher_id provided".

- 404 Not Found:
  - When referencing a student/course/teacher id that doesn't exist.

- Port already in use / server won't start:
  - Change port with uvicorn server:app --port 8001 or kill the process using the port.

- GUI cannot connect:
  - Make sure the API server is running and reachable at the address set in main.py as API_BASE (default "http://127.0.0.1:8000/api").
  - If running server on a different host or port, update API_BASE in main.py.

- If using GUI on a machine without display (headless / SSH): Tkinter GUI needs a display; run locally or use remote desktop.

Development tips & next steps
-----------------------------
- Add Alembic for database migrations if you plan to change the schema in production.
- Add authentication if you want to restrict endpoints.
- Add pagination/filters to list endpoints (already supports skip/limit).
- Add more robust validation or transactional behaviors in crud functions.
- Add tests: use pytest + TestClient (from fastapi.testclient) to test API endpoints.

Extending the GUI
-----------------
- The current Tkinter client is a simple demo. You can:
  - Add edit/delete operations in the GUI (create forms to call PUT and DELETE).
  - Add search or selection by clicking list entries.
  - Add better error display parsing response JSON message.

API documentation & exploration
------------------------------
- FastAPI automatically generates interactive docs:
  - Swagger UI: http://127.0.0.1:8000/docs
  - ReDoc: http://127.0.0.1:8000/redoc

Security & production notes
---------------------------
- SQLite is suitable for development or small-scale usage. For production, switch to PostgreSQL or MySQL and configure connection string accordingly.
- Ensure proper CORS configuration if you serve a web frontend from a different origin.
- Do not run uvicorn with --reload in production.
- Use environment variables for configuration (DB URL, host/port) instead of hard-coded values for production.

Appendix: Minimal server.py (recap)
----------------------------------
Save as server.py in the project root (example shown earlier). This file makes sure DB tables are created and the API router is mounted under /api.

Appendix: Quick start checklist
-------------------------------
1. Create & activate virtualenv.
2. pip install fastapi uvicorn sqlalchemy pydantic requests email-validator
3. Create server.py if not present (see example).
4. Start API:
   uvicorn server:app --reload --port 8000
5. In another terminal, run GUI:
   python main.py
6. Use GUI or visit http://127.0.0.1:8000/docs to try the API.

If you want, I can:
- Provide a ready-to-run server.py file created in your repo.
- Provide a docker-compose setup to run the API and GUI (GUI would require X11 forwarding; typically not containerized for desktop clients).
- Add unit tests and a CI workflow.

Would you like me to add server.py into the repo and update README with exact run commands?