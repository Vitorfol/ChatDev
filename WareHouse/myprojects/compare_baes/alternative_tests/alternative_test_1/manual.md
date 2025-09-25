# ChatDev — School API (User Manual)

ChatDev School API is a minimal backend + viewer project that demonstrates an incremental data model and API for Students, Courses, Enrollments and Teachers. It uses Python 3.11, FastAPI for the HTTP API, SQLAlchemy ORM + SQLite for persistence, Pydantic schemas, a small in-process migration system, and a tiny Streamlit UI to inspect database tables. A small automated smoke/regression test suite (pytest) is included.

This manual explains how to install dependencies, run the app, examine the DB with Streamlit, run tests, and use the API (examples and payloads). It also documents the core files and helpful troubleshooting tips.

Contents
- Quick prerequisites
- Install & prepare environment
- Project layout (key files)
- Start the API server
- API endpoints (summary + examples)
- Minimal Streamlit viewer
- Migrations (how they work & apply without restart)
- Tests (run smoke/regression)
- Resetting / reinitializing DB
- Troubleshooting & notes
- Extending the project

Quick prerequisites
- Python 3.11
- Git (optional)
- Unix-like shell or Windows PowerShell / cmd

Install & prepare environment

1) Create and activate a virtual environment (recommended)
- Unix / macOS:
  - python3.11 -m venv .venv
  - source .venv/bin/activate
- Windows (PowerShell):
  - python -m venv .venv
  - .\.venv\Scripts\Activate.ps1

2) Install Python dependencies
Run from the project root (where main.py and requirements below exist):

pip install fastapi uvicorn sqlalchemy "pydantic>=1" streamlit pandas pytest

(Optionally you can create a `requirements.txt` file with these lines and run `pip install -r requirements.txt`.)

Notes on packages:
- FastAPI includes Starlette and test client support.
- SQLite is built into Python, so no external DB server needed.
- The Streamlit UI uses pandas to render tables.

Project layout (key files)
- main.py — FastAPI entrypoint. Sets up engine, applies migrations on startup, registers routers.
- db.py — SQLAlchemy engine and Session management. Enables SQLite PRAGMA foreign_keys.
- migrate.py — Simple in-process SQL migration runner (applies .sql files found in migrations/ and records them in migrations table).
- migrations/
  - 001_create_student.sql
  - 002_add_student_email.sql
  - 003_create_course.sql
  - 004_create_enrollment.sql
  - 005_create_teacher.sql
  - 006_create_course_teacher.sql
- models.py — SQLAlchemy ORM models: Student, Course, Enrollment, Teacher, CourseTeacher.
- schemas.py — Pydantic models for request/response.
- students.py — Router for student CRUD endpoints.
- courses.py — Router for course CRUD endpoints.
- enrollments.py — Router to create/list/get/delete enrollments (explicit join table).
- teachers.py — Router for teacher CRUD endpoints.
- course_teachers.py — Router to assign/remove teachers to/from courses.
- streamlit_app.py — Tiny Streamlit UI to inspect tables.
- test_smoke.py — pytest-based smoke/regression test (FastAPI TestClient).
- chatdev.db — (created at runtime) SQLite DB file.
- commits.log — simulated commit history showing incremental changes.

Starting the API server (development)

1) Ensure virtual environment activated and dependencies installed.

2) Start the FastAPI app using Uvicorn:

uvicorn main:app --reload --host 127.0.0.1 --port 8000

Behavior:
- On startup the app will create/connect to `chatdev.db` (placed in the project root) and call apply_migrations(...) which executes SQL files inside `migrations/` in alphabetical order and records applied migrations in the `migrations` table.
- After that the server is ready to accept API requests.

Interactive API docs:
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

API endpoints (summary + examples)

Base URL: http://127.0.0.1:8000

General note: All endpoints return JSON unless a 204 No Content is used on deletes.

1) Students
- POST /students/ — Create student
  - Body: {"name": "Alice", "email": "alice@example.com"}
  - Returns: 201 Created with StudentRead: {"id": 1, "name": "...", "email": "..."}
- GET /students/ — List students (query params: skip, limit)
- GET /students/{student_id} — Get one student
- PUT /students/{student_id} — Update student (payload may include name and/or email)
  - Body example: {"name": "Alice B.", "email": "aliceb@example.com"}
- DELETE /students/{student_id} — Delete student (204)

curl examples:
- Create:
  curl -X POST "http://127.0.0.1:8000/students/" -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'
- Get all:
  curl "http://127.0.0.1:8000/students/"

2) Courses
- POST /courses/ — Create course
  - Body: {"title": "Intro to Testing", "level": "Beginner"}
- GET /courses/
- GET /courses/{course_id}
- PUT /courses/{course_id} — Update course (title and/or level)
- DELETE /courses/{course_id}

curl example:
  curl -X POST "http://127.0.0.1:8000/courses/" -H "Content-Type: application/json" -d '{"title":"Intro","level":"Beginner"}'

3) Enrollments (explicit many-to-many table)
- POST /enrollments/ — Enroll a student in a course
  - Body: {"student_id": 1, "course_id": 2}
  - Ensures student & course exist; uniqueness enforced.
- GET /enrollments/
- GET /enrollments/{enrollment_id}
- DELETE /enrollments/{enrollment_id}

4) Teachers
- POST /teachers/ — Create teacher
  - Body: {"name": "Dr. Smith", "department": "Computer Science"}
- GET /teachers/
- GET /teachers/{teacher_id}
- PUT /teachers/{teacher_id}
- DELETE /teachers/{teacher_id}

5) Course-Teacher assignments
- POST /course-teachers/ — Assign teacher to course
  - Body: {"course_id": 1, "teacher_id": 2}
  - Uniqueness enforced (course_id, teacher_id).
- GET /course-teachers/
- GET /course-teachers/{assignment_id}
- DELETE /course-teachers/{assignment_id}

Error codes / behavior
- 404 Not Found when resource missing.
- 400 Bad Request for duplicate enrollment/assignment.
- 201 Created for successful creates, 204 on successful deletes.

Minimal Streamlit viewer (inspect DB tables)

Purpose: tiny viewer to see table contents quickly.

Run Streamlit UI:

streamlit run streamlit_app.py

- Opens a simple page with a select box to choose one of: student, course, teacher, enrollment, course_teacher.
- Displays all rows (if any) using pandas.DataFrame.

Migrations — how they work & applying migrations without restarting

Migrations are SQL files stored in the `migrations/` directory (ordered alphabetically). The included migration runner (migrate.py) performs:
- Creates a `migrations` table to track applied migrations.
- Applies .sql files in sorted order which are not yet recorded in the `migrations` table.
- Records migration names with applied_at timestamp.
- The runner sanitizes files to avoid accidental triple-quoted Python blocks in SQL files.

By default the migrations are applied automatically when the FastAPI app starts (main.py calls apply_migrations during startup). This makes first-run setup automatic.

Applying new migrations without restarting the server:
- The migration runner is a plain Python function and can be invoked at runtime from a Python process to apply newly-added .sql files (this allows "in-process" application of migrations). Example run from project root:

python -c "from migrate import apply_migrations; import os; apply_migrations(os.path.join(os.getcwd(),'chatdev.db'), os.path.join(os.getcwd(),'migrations'))"

This will open the DB and apply any new .sql files placed into migrations/ without restarting the running FastAPI process. (If you prefer, you can add a simple API endpoint to call apply_migrations(...) inside the running server — currently the project applies migrations automatically at startup and lets you invoke the function manually as shown.)

Reset DB / Reinitialize
- Delete the DB file and restart the server (or run apply_migrations to recreate tables).
  - rm chatdev.db
  - Restart: uvicorn main:app --reload
- If you prefer to keep chatdev.db but wish to remove all data and migration records, you can open sqlite3 and drop tables, but deleting the `chatdev.db` file is simpler.

Run tests (smoke/regression)
- The project includes a pytest test: test_smoke.py which uses FastAPI's TestClient to perform a basic CRUD workflow.
- Run:

pytest -q

Notes:
- The TestClient will trigger application startup and apply migrations, so tests will operate against a fresh or existing chatdev.db. If you want a truly clean DB for tests, delete chatdev.db first.
- The test performs create-read-update-delete flows for students, courses, enrollments, teachers and assignments.

Troubleshooting & tips

- Port already in use: change the --port parameter when starting uvicorn.
- Foreign key constraints not enforced: db.py registers a listener to set PRAGMA foreign_keys=ON on each connection. If you get integrity problems, ensure the engine in db.get_engine is used (main.py creates engine from get_engine and calls init_db_session).
- Migration fails with weird triple-quoted blocks: migrate.py sanitizes these, but ensure your SQL files contain pure SQL. Keep SQL comments using SQL-style `-- comment`.
- To re-run a migration that failed: fix migration SQL file, remove the entry from the `migrations` table for that migration (or delete the DB), then re-run apply_migrations.
  - Example to remove a migration record in sqlite3:
    sqlite3 chatdev.db "DELETE FROM migrations WHERE name='your_migration.sql';"
- If Streamlit shows “No data or table missing.” ensure migrations were applied and chatdev.db exists.

Security & production notes
- This project is for demonstration / local development. There is no authentication/authorization; do not expose to untrusted networks without adding proper security.
- For production, consider:
  - Using PostgreSQL or another robust RDBMS.
  - Adding migrations management tooling (Alembic).
  - Adding proper logging and error handling.
  - Adding authentication and rate limiting.

Example end-to-end workflow
1. Create virtualenv & install dependencies.
2. Start the API:
   uvicorn main:app --reload
3. Use Swagger UI: http://127.0.0.1:8000/docs
4. Create student, course, teacher using POST endpoints.
5. Create enrollment and assignment via POST /enrollments/ and POST /course-teachers/
6. Inspect DB via Streamlit:
   streamlit run streamlit_app.py
7. Run the smoke test:
   pytest -q

Commit / incremental development notes
- The project was built incrementally (see commits.log) — each feature addition (student, student email, course, enrollment, teacher, course-teacher) was delivered with a migration SQL and updated models + routers.
- The migration runner ensures migrations are recorded and not re-applied.

Extending the project
- Add more fields (e.g., Student.date_of_birth): create a SQL migration file in migrations/ (e.g., 007_add_student_dob.sql) and add corresponding column to models.py + update schemas.py. Then either restart the server (apply at startup) or run the one-liner to call apply_migrations(...) without restart.
- Add search/filters to list endpoints, paginated responses, or joins to return nested objects (e.g., course with assigned teachers).
- Add an API endpoint to trigger apply_migrations remotely (secure it) if you want a HTTP-based migration trigger.

Appendix — Summary of API endpoints (quick reference)
- Students
  - POST /students/
  - GET /students/
  - GET /students/{student_id}
  - PUT /students/{student_id}
  - DELETE /students/{student_id}
- Courses
  - POST /courses/
  - GET /courses/
  - GET /courses/{course_id}
  - PUT /courses/{course_id}
  - DELETE /courses/{course_id}
- Enrollments
  - POST /enrollments/
  - GET /enrollments/
  - GET /enrollments/{enrollment_id}
  - DELETE /enrollments/{enrollment_id}
- Teachers
  - POST /teachers/
  - GET /teachers/
  - GET /teachers/{teacher_id}
  - PUT /teachers/{teacher_id}
  - DELETE /teachers/{teacher_id}
- Course-Teacher Assignments
  - POST /course-teachers/
  - GET /course-teachers/
  - GET /course-teachers/{assignment_id}
  - DELETE /course-teachers/{assignment_id}

License & acknowledgements
- This example is provided as-is for demonstration and educational purposes. Adapt and extend as needed.

If you want, I can:
- Produce a sample requirements.txt or a Dockerfile for containerized runs.
- Add a small CLI script to apply migrations and show status.
- Add an authenticated migration-trigger endpoint (secured with a token).