# School Management — User Manual

This repository provides a small school management system built with:
- FastAPI (backend API)
- SQLAlchemy + SQLite (persistence)
- Pydantic schemas (validation)
- A simple Tkinter desktop client (GUI) to interact with the API

Main capabilities:
- CRUD for Students, Courses, Teachers
- Student email field (validated and unique)
- Course level attribute (e.g., "Beginner", "Intermediate", "Advanced")
- Relationships:
  - Student <-> Course: many-to-many (enroll/unenroll)
  - Teacher -> Course: one-to-many (assign/unassign)
- Simple GUI (Tkinter) with tabs for Students, Courses, Teachers and basic operations

This manual explains how to install, run, and use the system (API and GUI) and includes example API calls and troubleshooting notes.

Table of contents
- Quick summary / features
- Repository structure (key files)
- Prerequisites
- Install and setup
- Run the API server
- Run the GUI client
- API reference with example requests
- Database persistence and notes
- Troubleshooting
- Development & deployment notes (Docker, migrations, improvements)
- Contact / support

---

## Quick summary / features

- Students: create/read/update/delete. Email is required, validated, and unique. View enrolled courses. Enroll/unenroll in courses.
- Courses: create/read/update/delete. Has `title`, `description`, and `level`. Can optionally be assigned to a Teacher. See enrolled Students.
- Teachers: create/read/update/delete. Optional email. View courses taught.
- Storage: local SQLite database `school.db` (by default in project root).
- Simple desktop GUI wraps common operations (create, list, assign, enroll, etc.).

---

## Repository structure (key files)

- api.py — FastAPI application (all endpoints). Automatically creates DB tables on start.
- database.py — SQLAlchemy engine, SessionLocal, Base. Uses SQLite (`sqlite:///./school.db`).
- models.py — SQLAlchemy ORM models:
  - Student (id, name, email, courses)
  - Teacher (id, name, email, courses)
  - Course (id, title, description, level, teacher_id, students)
  - Association table student_course for many-to-many
- schemas.py — Pydantic request/response schemas (EmailStr validation, ORM mode).
- crud.py — Database access helpers (CRUD and relationship functions).
- main.py — Simple Tkinter GUI client that talks to the API at http://127.0.0.1:8000
- requirements.txt — Python dependencies
- manual.md — This user manual

---

## Prerequisites

- Python 3.8+ (recommended 3.9/3.10/3.11)
- pip
- (Optional) virtualenv or conda for isolated environment
- For Docker-based run: Docker & docker-compose (optional)

Dependencies (will be installed by pip):
- fastapi
- uvicorn
- SQLAlchemy
- pydantic
- requests

---

## Install and setup

1. Clone the repository and change to the project directory:
   ```
   git clone <repo-url>
   cd <repo-directory>
   ```

2. Create and activate a virtual environment (recommended):
   - macOS / Linux:
     ```
     python3 -m venv .venv
     source .venv/bin/activate
     ```
   - Windows (PowerShell):
     ```
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. (Optional) Verify Python & pip versions:
   ```
   python --version
   pip --version
   ```

---

## Run the API server

Start the FastAPI server with uvicorn. From the project root:

```
uvicorn api:app --reload
```

- The server will be available at: http://127.0.0.1:8000
- Automatic OpenAPI docs: http://127.0.0.1:8000/docs
- The code in `api.py` calls `models.Base.metadata.create_all(bind=database.engine)` on import — tables will be created automatically in `school.db`.

Notes:
- For production, do not use `--reload` (dev only) and use a production-ready ASGI server setup or container.
- If you wish to change host/port:
  ```
  uvicorn api:app --host 0.0.0.0 --port 8080
  ```

---

## Run the GUI client (Tkinter)

1. Ensure the API server is running (see above).
2. Run the GUI script:
   ```
   python main.py
   ```
3. The GUI is a desktop window with three tabs:
   - Students
   - Courses
   - Teachers

GUI functionality (summary):
- Students tab:
  - Create Student (Name + Email)
  - Refresh list
  - Select a student and:
    - Enroll in a course (opens a course selector)
    - Unenroll from a course (shows student’s courses)
    - Show student’s courses (popup lists titles and levels)
- Courses tab:
  - Create Course (Title, Description, Level, optional Teacher ID)
  - Refresh list
  - Select a course and:
    - Assign Teacher (enter Teacher ID)
    - Show enrolled students
- Teachers tab:
  - Create Teacher (Name, Email optional)
  - Refresh list
  - Select a teacher and show courses they teach

GUI expects API at `http://127.0.0.1:8000` (see API_URL in `main.py`). If your API runs elsewhere, update API_URL in `main.py`.

---

## API reference (endpoints & examples)

General notes:
- All responses use the Pydantic schemas in `schemas.py`. Many responses use `orm_mode=True`, so SQLAlchemy models are returned through the schemas.
- Student email is validated and unique.
- Course `level` is a string (optional).

Base URL (default): http://127.0.0.1:8000

Examples below use curl. You can also use the interactive docs at /docs or tools like Postman.

1) Students
- List students
  ```
  GET /students/
  curl http://127.0.0.1:8000/students/
  ```
  Response: JSON array of students with id, name, email, and courses (each course limited fields via CourseSimple).

- Create student
  ```
  POST /students/
  curl -X POST http://127.0.0.1:8000/students/ -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'
  ```
  Returns created student (201). If email already used you'll get 400.

- Get single student
  ```
  GET /students/{student_id}
  curl http://127.0.0.1:8000/students/1
  ```

- Update student
  ```
  PUT /students/{student_id}
  curl -X PUT http://127.0.0.1:8000/students/1 -H "Content-Type: application/json" -d '{"name":"Alice L."}'
  ```

- Delete student
  ```
  DELETE /students/{student_id}
  curl -X DELETE http://127.0.0.1:8000/students/1
  ```

- List student's courses
  ```
  GET /students/{student_id}/courses
  ```

- Enroll student in a course
  ```
  POST /students/{student_id}/enroll/{course_id}
  curl -X POST http://127.0.0.1:8000/students/1/enroll/2
  ```

- Unenroll student from a course
  ```
  DELETE /students/{student_id}/unenroll/{course_id}
  curl -X DELETE http://127.0.0.1:8000/students/1/unenroll/2
  ```

2) Courses
- List courses
  ```
  GET /courses/
  curl http://127.0.0.1:8000/courses/
  ```

- Create course
  ```
  POST /courses/
  curl -X POST http://127.0.0.1:8000/courses/ -H "Content-Type: application/json" -d '{"title":"Algebra I","description":"Basic algebra","level":"Beginner", "teacher_id": 1}'
  ```
  If teacher_id provided and not found => 400.

- Get course (includes students and teacher)
  ```
  GET /courses/{course_id}
  ```

- Update course
  ```
  PUT /courses/{course_id}
  # To unassign teacher set teacher_id = 0
  curl -X PUT http://127.0.0.1:8000/courses/2 -H "Content-Type: application/json" -d '{"level":"Intermediate", "teacher_id": 0}'
  ```

- Delete course
  ```
  DELETE /courses/{course_id}
  ```

- Assign teacher to course
  ```
  POST /courses/{course_id}/assign_teacher/{teacher_id}
  curl -X POST http://127.0.0.1:8000/courses/2/assign_teacher/1
  ```

3) Teachers
- List teachers
  ```
  GET /teachers/
  ```

- Create teacher
  ```
  POST /teachers/
  curl -X POST http://127.0.0.1:8000/teachers/ -H "Content-Type: application/json" -d '{"name":"Dr. Smith","email":"smith@example.com"}'
  ```

- Get teacher
  ```
  GET /teachers/{teacher_id}
  ```

- Update teacher
  ```
  PUT /teachers/{teacher_id}
  ```

- Delete teacher
  ```
  DELETE /teachers/{teacher_id}
  # Courses taught by this teacher will have teacher unassigned (teacher set to null)
  ```

- List teacher's courses
  ```
  GET /teachers/{teacher_id}/courses
  ```

---

## Database persistence & important notes

- Default DB file: ./school.db (SQLite). The connection string is in database.py:
  ```
  SQLALCHEMY_DATABASE_URL = "sqlite:///./school.db"
  ```
- Tables are auto-created at API start because `models.Base.metadata.create_all(bind=database.engine)` is executed in api.py.
- SQLite concurrency: SQLite is not ideal for high-concurrency writes. The app is intended for small/demo usage. For production consider PostgreSQL or MySQL and use Alembic for migrations.

Email uniqueness:
- Student.email is unique; trying to create a student with an existing email will return 400.
- Teacher.email is unique if provided.

Data relationships:
- Removing a student or course will remove many-to-many associations before deleting.
- Deleting a teacher will unassign them from courses (teacher set to null).

---

## Troubleshooting

- API not reachable:
  - Ensure `uvicorn api:app --reload` is running.
  - Check port/host. GUI expects http://127.0.0.1:8000 by default. Change `API_URL` in main.py if your server runs elsewhere.

- GUI errors like "Failed to reach API":
  - Server likely not running or network issues.

- SQLite "check_same_thread" errors:
  - database.py sets `connect_args={"check_same_thread": False}` to allow multiple threads. Do not change unless you know what you’re doing.

- Unique constraint errors:
  - Creating another student/teacher with same email will fail. Use unique emails.

- Changes not persisting:
  - Check that the DB file `school.db` is in the project root. If you accidentally run the server from another directory the DB might be created elsewhere.

- Deleting entities:
  - Deleting a student removes their course associations first. Deleting a teacher unassigns their courses.

---

## Development & deployment notes

- Use Alembic for structured DB migrations if evolving schema over time (recommended for production).
- For production database, switch to PostgreSQL/MySQL and update `database.py` connection string.
- Docker example (basic):
  - Dockerfile (example)
    ```
    FROM python:3.11-slim
    WORKDIR /app
    COPY . /app
    RUN pip install --no-cache-dir -r requirements.txt
    EXPOSE 8000
    CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
    ```
  - docker build -t school-api .
  - docker run -p 8000:8000 school-api

- Logging:
  - Add and configure logging for server-side debugging.

- Tests:
  - Add unit tests for CRUD and endpoints using pytest + fastapi.testclient for robust CI.

- Security:
  - This example exposes endpoints without authentication. Add OAuth2/JWT or similar (FastAPI supports OAuth2 flows).
  - Validate user input and rate-limit in production.

---

## Suggestions for next improvements

- Add pagination and filtering on listing endpoints.
- Add search endpoints (by name, email, course level).
- Add an enrollment date attribute (for auditing).
- Add login/auth and role-based permissions (admin vs teacher vs student).
- Improve GUI: persistent selection, editing entities from GUI, better UX.
- Add file-based export/import (CSV) to export lists.
- Add tests and CI/CD (GitHub Actions).

---

## Example walk-through (basic scenario)

1. Start API:
   ```
   uvicorn api:app --reload
   ```

2. Create a teacher:
   ```
   curl -X POST http://127.0.0.1:8000/teachers/ -H "Content-Type: application/json" -d '{"name":"Ms. Green","email":"green@example.com"}'
   ```

3. Create a course and assign teacher (teacher_id from previous step, e.g., 1):
   ```
   curl -X POST http://127.0.0.1:8000/courses/ -H "Content-Type: application/json" -d '{"title":"Biology 101", "description":"Intro", "level":"Beginner", "teacher_id": 1}'
   ```

4. Create a student:
   ```
   curl -X POST http://127.0.0.1:8000/students/ -H "Content-Type: application/json" -d '{"name":"Bob", "email":"bob@example.com"}'
   ```

5. Enroll the student in the course (use appropriate IDs):
   ```
   curl -X POST http://127.0.0.1:8000/students/1/enroll/1
   ```

6. Check student's courses:
   ```
   curl http://127.0.0.1:8000/students/1/courses
   ```

You can perform the same steps using the GUI: create teacher, create course (specify teacher ID), create student, select student, enroll in course.

---

## Contact / support

If you need help:
- Check the FastAPI docs: https://fastapi.tiangolo.com/
- For SQLAlchemy & migrations: https://docs.sqlalchemy.org/
- If this repository is internal to ChatDev, open an issue in the project tracker or contact the team lead for help.

---

End of manual.

If you want, I can also:
- Provide a ready-to-use Docker Compose file,
- Create an Alembic migration template for schema evolution,
- Generate a small Postman collection with these endpoints.