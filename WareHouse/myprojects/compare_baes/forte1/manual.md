# Academic Management System — User Manual

This repository implements a small academic management backend in Python with an emphasis on incremental, zero-downtime schema evolution (migrations) and a domain-driven design (DDD) separation of concerns. It includes:

- FastAPI-based HTTP CRUD endpoints for Students, Courses, Enrollments, Teachers, and Teachings.
- A MigrationManager that applies ordered in-process SQLite schema migrations and can mount new API routers at runtime (simulate zero-downtime evolution).
- Repositories (direct SQL), Services (domain logic), and Pydantic Schemas (API boundary).
- A minimal Streamlit UI for inspecting the live SQLite DB.
- A small automated smoke test that drives the migration sequence and verifies CRUD behavior end-to-end.

This manual explains the architecture, dependencies, how to install and run the system, how to drive migrations, and how to run the smoke test and the Streamlit inspector.

Contents
- Quick summary
- Architecture & file overview
- Requirements & installation
- App wiring (creating the FastAPI app entrypoint)
- Running the API server (development)
- Driving migrations and example usage (curl)
- Streamlit inspector
- Running the automated smoke test
- Resetting the database and troubleshooting
- Design notes and guarantees

Quick summary
- Python 3.11 recommended.
- Use the MigrationManager to apply migrations one-by-one via POST /migrate/next.
- The API grows incrementally; endpoints are mounted as migrations are applied.
- Database file: academic.db (in the repo root). Delete it to reset to empty state.

Architecture & file overview
- db.py
  - sqlite3 helper: get_db_path(), connect_db(). Enables fresh connections per operation and enforces PRAGMA foreign_keys.
- schemas.py
  - Pydantic models used at the API boundary. Uses optional fields to tolerate incremental schema changes.
- repositories.py
  - Direct SQL access layer (Repository pattern) that encapsulates SQL logic and raw queries.
- services.py
  - Domain services that call repositories. Preserve docstrings and semantic vocabulary.
- api.py
  - APIRouter instances for Students, Courses, Enrollments, Teachers, Teachings and a migration control route.
  - Student endpoints are expected to be available initially; other routers are mounted by migrations.
- migrate.py
  - MigrationManager implements the ordered migrations 001 → 006. Migrations apply SQL changes and mount routers on the running FastAPI app.
  - Migration names:
    - 001_create_student
    - 002_add_student_email
    - 003_create_course
    - 004_create_enrollment
    - 005_create_teacher
    - 006_create_teaching
- streamlit_app.py
  - Minimal Streamlit app that reads tables (if present) and prints rows for inspection.
- main.py (provided as a smoke test in the repository)
  - IMPORTANT: The repository includes a file named main.py which is an automated smoke test that expects the running FastAPI app to be importable as `main.app` and a migration manager as `main.migration_manager`. If you prefer to keep the smoke test separate from your app entrypoint, rename this file to smoke_test.py. See "Running the automated smoke test" below.

Requirements & installation
1. Create a virtual environment (recommended)
   - python -m venv .venv
   - Unix/macOS: source .venv/bin/activate
   - Windows (PowerShell): .venv\Scripts\Activate.ps1

2. Install required packages
   Minimal set:
   - fastapi
   - uvicorn
   - streamlit
   - requests
   - pydantic

   Example:
   - pip install fastapi uvicorn streamlit requests

   Alternatively to get test client and all extras:
   - pip install "fastapi[all]" uvicorn streamlit

3. Python standard libraries used: sqlite3, os, typing, time — no extra installation required for those.

App wiring: create the FastAPI entrypoint
The migration manager expects to mount routers at runtime onto a FastAPI app and to be accessible via import. If your repository does not yet have a FastAPI app entrypoint exposing `app` and `migration_manager` as expected by the smoke-test, create a small `app_main.py` (or `main_app.py`) file with the following content:

```python
# app_main.py
from fastapi import FastAPI
from api import students_router, migration_router
from migrate import MigrationManager
from db import get_db_path

app = FastAPI(title="Academic Management (incremental migrations demo)")

# Student APIs are usable at the start (migration 001 creates the table; router present)
app.include_router(students_router)

# Expose the migration control endpoint so clients/tests can apply next migration
app.include_router(migration_router, prefix="/migrate")

# Create the MigrationManager and attach it to the app for global access
migration_manager = MigrationManager(app=app, db_path=get_db_path())
# (Note: MigrationManager ensures its migrations table exists on init.)
```

Notes:
- The Student router is included initially because migration 001 only creates the table; the router needs to exist to accept student-related requests right away. The MigrationManager mounts additional routers during migrations.
- If you prefer, name the file `main.py` so uvicorn can run `uvicorn main:app` — but if your repo's main.py is the smoke test, rename the smoke test first (see below).

Running the API server (development)
Assuming you saved the entrypoint as app_main.py:

- Start the server with uvicorn in the venv:
  - uvicorn app_main:app --reload --port 8000

If you named the entrypoint main.py and it exposes `app`, run:
  - uvicorn main:app --reload --port 8000

The server will start with only the initial routers included (Students + migration control). The other routers (courses, enrollments, teachers, teachings) will be mounted progressively when you POST to the migration endpoint.

Driving migrations and example usage
The MigrationManager applies migrations in order when you POST to /migrate/next. Each call applies exactly one new migration (if pending) and returns a JSON payload describing which migration was applied.

Example: apply the first migration (create student table)
- curl -X POST http://127.0.0.1:8000/migrate/next
- Response:
  - {"applied": "001_create_student"}

After that, the Student API is available (the Student router is included initially by your app entrypoint):

Create a student (POST /students)
- curl -X POST http://127.0.0.1:8000/students -H "Content-Type: application/json" -d '{"id": 1}'
- Response: 201 Created: {"id":1,"email":null}

Get a student (GET /students/{id})
- curl http://127.0.0.1:8000/students/1

Apply migration 002 (add email column)
- curl -X POST http://127.0.0.1:8000/migrate/next
- Response: {"applied":"002_add_student_email"}

Update a student with email
- curl -X PUT http://127.0.0.1:8000/students/1 -H "Content-Type: application/json" -d '{"email":"alice@example.com"}'

Apply migration 003 (create courses and mount /courses)
- curl -X POST http://127.0.0.1:8000/migrate/next
- Response: {"applied":"003_create_course"}

Create & get courses:
- POST /courses, GET /courses/{id}, PUT /courses/{id}, etc.

Apply migration 004 (create enrollment table and mount /enrollments)
- curl -X POST http://127.0.0.1:8000/migrate/next
- Use POST /enrollments to create a student→course enrollment.

Apply migration 005 (create teacher table and mount /teachers)
- curl -X POST http://127.0.0.1:8000/migrate/next

Apply migration 006 (create teaching table and mount /teachings)
- curl -X POST http://127.0.0.1:8000/migrate/next
- Then use /teachings endpoints.

API endpoints summary (once mounted)
- Students (initial router)
  - POST /students {id, email?}
  - GET /students
  - GET /students/{student_id}
  - PUT /students/{student_id} {email?}
  - DELETE /students/{student_id}
- Courses (mounted by 003_create_course)
  - POST /courses {id, level?}
  - GET /courses
  - GET /courses/{course_id}
  - PUT /courses/{course_id} {level?}
  - DELETE /courses/{course_id}
- Enrollments (mounted by 004_create_enrollment)
  - POST /enrollments {student_id, course_id}
  - GET /enrollments
  - GET /enrollments/{enrollment_id}
  - DELETE /enrollments/{enrollment_id}
- Teachers (mounted by 005_create_teacher)
  - POST /teachers {id}
  - GET /teachers
  - GET /teachers/{teacher_id}
  - DELETE /teachers/{teacher_id}
- Teachings (mounted by 006_create_teaching)
  - POST /teachings {teacher_id, course_id}
  - GET /teachings
  - GET /teachings/{teaching_id}
  - DELETE /teachings/{teaching_id}
- Migrations (control endpoint)
  - POST /migrate/next
    - Applies the next pending migration. Response: {"applied": "<migration_name>"} or {"applied": null, "message": "No pending migrations."}

Streamlit inspector
- Purpose: Minimal read-only UI to inspect whichever tables currently exist in the DB.
- Run:
  - streamlit run streamlit_app.py
- Point-of-attention:
  - streamlit_app.py opens the SQLite database used by the API (academic.db); make sure the server uses the same DB file path. The db.py helper uses "academic.db" in the repo root by default.
  - The Streamlit app lists tables among: student, course, teacher, enrollment, teaching, migrations and shows row tuples. It is intentionally minimal.

Running the automated smoke test
- The repository contains an automated smoke test script (currently named main.py in the code listing). This script expects to import the running FastAPI app and the migration_manager from an application module named `main` — i.e., it expects `main.app` and `main.migration_manager` to exist in the import path.
- If you followed the suggested app wiring above and named your entrypoint app_main.py, rename or edit the smoke test to import `app_main` instead of `main`, or move the entrypoint snippet into `main.py` so it exposes `app` and `migration_manager`.

Recommended approach:
1. If `main.py` currently contains the smoke test, rename it to smoke_test.py:
   - git mv main.py smoke_test.py
   - or save the file under smoke_test.py

2. Create app entrypoint file main.py with the "App wiring" snippet above so that `main.app` and `main.migration_manager` are available.

3. Start the server:
   - uvicorn main:app --reload --port 8000

4. Run the smoke test:
   - python smoke_test.py
   - The smoke test uses FastAPI TestClient to run the sequence: apply migrations one-by-one and perform CRUD checks. On success: prints "SMOKE TEST PASSED".

Notes:
- If your environment does not have FastAPI installed, the smoke test has safeguards to explain how to install dependencies and will skip gracefully.
- The smoke test deletes the DB file first (if present) to ensure a clean test run.

Resetting the database and re-running
- Delete the DB file to start from scratch:
  - rm academic.db
- Re-apply migrations by POSTing to /migrate/next repeatedly (or run the smoke test which will do it for you).

Troubleshooting & common pitfalls
- Router mounting not visible
  - Ensure your entrypoint includes students_router at start (students Router provides endpoints for migration 1).
  - MigrationManager mounts other routers when their migrations run. Confirm the server process has the same MigrationManager instance referenced by the migration control route.
- “Table does not exist” errors
  - This means the migration that creates that table has not been applied yet. Apply next migration: POST /migrate/next.
- Import errors when running smoke test
  - The smoke test expects to import app/migration manager from a module named main (or change the import). Make sure names align or adjust file names.
- Foreign key constraint errors
  - The repositories/DB layer enables PRAGMA foreign_keys=ON. Ensure you create referenced parent rows before child rows (e.g., create Student and Course before Enrollment).

Design notes & guarantees
- Domain-driven design (DDD):
  - Repositories handle SQL details.
  - Services provide domain-level functions with preserved docstrings and semantic naming.
  - Pydantic schemas standardize the API contract.
- Incremental migrations:
  - Migrations are idempotent and recorded in a simple `migrations` table.
  - Migrations modify the SQLite schema and, when appropriate, mount routers on the running FastAPI app to expand the public API surface without restarting.
- Zero-downtime approach:
  - The MigrationManager operates in-process and calls app.include_router(...) to add endpoints dynamically.
  - The database file is used by fresh sqlite3 connections to avoid long-lived metadata issues.
- Testing:
  - The included smoke test drives migrations and basic CRUD flows in sequence to validate the intended incremental behavior.

Example quick workflow (step-by-step)
1. Prepare env & install dependencies.
2. Create main.py (FastAPI app + MigrationManager) if not already present.
3. Start server:
   - uvicorn main:app --reload
4. Apply migration sequence:
   - POST /migrate/next (repeat until "No pending migrations.")
5. Use mounted endpoints as they appear (students initially; courses after migration 003; enrollments after 004; etc.)
6. Inspect DB via Streamlit:
   - streamlit run streamlit_app.py
7. Run smoke test (if smoke_test.py is present and imports `main.app` and `main.migration_manager` correctly):
   - python smoke_test.py

Appendix: Useful commands
- Start server:
  - uvicorn main:app --reload --port 8000
- Apply next migration manually:
  - curl -X POST http://127.0.0.1:8000/migrate/next
- Create a student:
  - curl -X POST http://127.0.0.1:8000/students -H "Content-Type: application/json" -d '{"id": 1}'
- Create a course (after migration 003):
  - curl -X POST http://127.0.0.1:8000/courses -H "Content-Type: application/json" -d '{"id": 10, "level": "Undergrad"}'
- Create an enrollment (after migration 004):
  - curl -X POST http://127.0.0.1:8000/enrollments -H "Content-Type: application/json" -d '{"student_id":1,"course_id":10}'
- Streamlit inspector:
  - streamlit run streamlit_app.py
- Run automated smoke test (if named smoke_test.py):
  - python smoke_test.py

If you would like, I can:
- Provide a ready-to-save main.py entrypoint matching the smoke-test expectations,
- Provide a small requirements.txt,
- Or create a small Makefile with commands to run, test, and reset the DB.

Contact / support
This repository is intended as a demo of incremental schema evolution with simple app logic. If you want production hardening (migrations via Alembic, more robust concurrency, authentication, CI/CD), we can propose an implementation plan and timeline.