# Academic Management System — User Manual

This manual describes how to install, run, evolve, inspect and test the Academic Management System (Python 3.11, FastAPI, SQLite, SQLAlchemy, Pydantic, Streamlit). The project demonstrates zero-downtime, in-process schema evolution across six incremental migration steps while preserving a stable domain vocabulary (domain-driven design).

Contents
- Overview
- Quick requirements & install
- Files & architecture overview
- Running the FastAPI server
- Applying migrations (the 6-step incremental flow)
- Using the CRUD endpoints (examples)
- Streamlit inspector (UI)
- Smoke test (automated)
- Notes on zero-downtime / design
- Troubleshooting & tips
- Recommended requirements.txt

Overview
This project models an academic domain with these concepts:
- Student (id, email added in step 2)
- Course (id, level)
- Enrollment (student ↔ course relationship)
- Teacher (id)
- Teaching (teacher ↔ course relationship)

Schema is evolved in-process using a MigrationService that applies the following steps:
1. Create students (id PK)
2. Add students.email (TEXT)
3. Create courses (id PK, level TEXT)
4. Create enrollments (id PK, student_id FK, course_id FK)
5. Create teachers (id PK)
6. Create teachings (id PK, teacher_id FK, course_id FK)

The repository layer uses SQLAlchemy reflection at each operation so the running server adapts to new tables/columns without restart.

Quick requirements & install
- Python: 3.11 (tested)
- SQLite (bundled with Python)
- Recommended packages (pip):

  pip install fastapi uvicorn sqlalchemy pydantic streamlit aiosqlite

Alternatively, create a virtual environment:
- Create & activate venv
  python3.11 -m venv .venv
  source .venv/bin/activate  (Linux/macOS) or .venv\Scripts\activate (Windows)
- Install:
  pip install --upgrade pip
  pip install fastapi uvicorn sqlalchemy pydantic streamlit

(See the included recommended requirements.txt at the end of this manual.)

Files & architecture overview
- main.py
  - In this repository the file named main.py contains the automated smoke test tool (some project README references `smoke_test.py` — both names are used in drafts). When running the FastAPI server the entrypoint should be the application module that exposes `app` (see below).
  - If your project also contains a FastAPI app file named main.py, ensure the smoke test script is named smoke_test.py to avoid conflicts.
- api.py
  - FastAPI routers and endpoints for Students, Courses, Enrollments, Teachers, Teachings, migrations and smoke.
  - Exposes endpoints to create/read/update/delete domain objects and /migrate for in-process migration application.
- db.py
  - SQLite engine creation, PRAGMA enforcement (foreign keys), migration tracking table and reflection helpers.
- migrations.py
  - MigrationService: idempotent migration steps, records applied steps in `migrations` table.
- domain/entities.py
  - Stable Pydantic domain models (StudentIn/Out, CourseIn/Out, EnrollmentIn/Out, TeacherIn/Out, TeachingIn/Out).
- repositories.py
  - Data access layer using SQLAlchemy Core and reflection so it adapts to schema changes at runtime.
- services.py
  - Business logic / domain services calling repositories (validation such as ensuring referenced entities exist).
- streamlit_app.py
  - Minimal Streamlit UI to inspect tables/rows in academic.db.
- readme.md
  - Project overview & basic instructions.
- __init__.py
  - domain package initializer.

Starting the FastAPI server
1. Make sure your working directory contains the project files and your venv is active.
2. Start the FastAPI app (the code expects a module exposing an `app` FastAPI instance that imports `api` router). If your FastAPI app is in a file named app.py or server.py, adapt the command; a typical command:

   uvicorn main_app:app --reload

   Replace main_app with the module name that constructs the FastAPI app and includes:
   - include_router(api.router, prefix="") or similar import of api router.

   If this repo uses a dedicated entrypoint (e.g., app.py that includes from api import router and sets `app = FastAPI()`), then run:

   uvicorn app:app --reload

3. API docs:
   - After server start, open interactive docs: http://127.0.0.1:8000/docs

Applying migrations — incremental flow
The project uses in-process migrations so you can evolve the database while the server runs.

Endpoint:
- POST /migrate
  - payload: {"step": <n>} where n is integer 1..6
  - Example:

    curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":1}'

Recommendation: Apply steps sequentially (1 → 2 → 3 → 4 → 5 → 6). Each step is idempotent and recorded in the `migrations` table.

Suggested migration sequence for the 6 natural-language commands:
1. POST /migrate {"step": 1} — creates students table (id PK).
2. POST /migrate {"step": 2} — adds email column to students.
3. POST /migrate {"step": 3} — creates courses table (id PK, level).
4. POST /migrate {"step": 4} — creates enrollments table (id PK, student_id FK, course_id FK).
5. POST /migrate {"step": 5} — creates teachers table (id PK).
6. POST /migrate {"step": 6} — creates teachings table (id PK, teacher_id FK, course_id FK).

You can also query applied migrations:
- GET /migrations → returns {"applied_steps": [ ... ]}

Using the CRUD endpoints — examples
Carry out actions after applying the relevant migration(s).

Students
- Create student (after step 1; step 2 adds email support but the StudentIn model allows absence of email until step 2).
  curl -X POST "http://127.0.0.1:8000/students" -H "Content-Type: application/json" -d '{"id": null}'

  After step 2 you can create with an email:
  curl -X POST "http://127.0.0.1:8000/students" -H "Content-Type: application/json" -d '{"email":"alice@example.com"}'

- Get student:
  curl "http://127.0.0.1:8000/students/1"

- Update student (add or modify email):
  curl -X PUT "http://127.0.0.1:8000/students/1" -H "Content-Type: application/json" -d '{"email":"alice2@example.com"}'

- List:
  curl "http://127.0.0.1:8000/students"

- Delete:
  curl -X DELETE "http://127.0.0.1:8000/students/1"

Courses
- (After step 3)
- Create:
  curl -X POST "http://127.0.0.1:8000/courses" -H "Content-Type: application/json" -d '{"level":"Undergrad"}'
- Get, list, update, delete similar to students (using /courses and course ids).

Enrollments
- (After step 4)
- Create enrollment (student_id and course_id must exist):
  curl -X POST "http://127.0.0.1:8000/enrollments" -H "Content-Type: application/json" -d '{"student_id":1,"course_id":1}'
- Get/list/update/delete: /enrollments

Teachers
- (After step 5)
- Create:
  curl -X POST "http://127.0.0.1:8000/teachers" -H "Content-Type: application/json" -d '{}'
- Get/list/delete via /teachers

Teachings
- (After step 6)
- Create teaching (teacher_id and course_id must exist):
  curl -X POST "http://127.0.0.1:8000/teachings" -H "Content-Type: application/json" -d '{"teacher_id":1,"course_id":1}'
- Get/list/update/delete via /teachings

Streamlit inspector (minimal UI)
To inspect database tables and rows:
1. With the server running (or even without it), run:

   streamlit run streamlit_app.py

2. The Streamlit app shows known tables, columns and rows for the SQLite `academic.db`. It also suggests using the /migrate endpoint to evolve the schema.

Smoke test (automated)
There is an automated smoke test that exercises CRUD for Students, Courses, Enrollments, Teachers, Teachings. It expects migrations 1..6 applied.

How to run:
- Via API endpoint (if the server is running and the project exposes a smoke test import compatible with api.py):
  POST /smoke
  Example:
    curl -X POST "http://127.0.0.1:8000/smoke"

  Returns JSON: {"ok": true/false, "details": "..."}.

- Via command line script:
  If the project contains smoke_test.py or main.py as the smoke test runner, run:

    python main.py

  or

    python smoke_test.py

  The script will:
  - Ensure migrations up to step 6 are applied (migration_service.apply_up_to(6))
  - Create a student, course, create enrollment, create teacher, create teaching, update/verify, and clean up.
  - Print the test result and details.

Note: If the repository's `api.py` references `smoke_test` but the script file is named main.py (or vice versa), rename one to match the other to avoid import errors. Recommended: ensure the smoke test file is named smoke_test.py and that api.py imports from smoke_test import run_smoke_test.

Notes on zero-downtime / design
- Domain-driven design: domain/entities.py contains the canonical Pydantic models. These models are preserved across migrations to keep the vocabulary stable.
- Repositories use SQLAlchemy MetaData reflection (reflect_table) at each operation. That means adding a new column or table via migrations becomes visible to repositories without restarting the server.
- Migrations are applied in-process by MigrationService and recorded in `migrations` table to ensure idempotence and traceability.
- Basic domain validation in service layer: e.g., EnrollmentService.create ensures referenced student and course exist; TeachingService.create ensures teacher and course exist.

Troubleshooting & common issues
- Port conflict: If uvicorn fails to start on 8000, specify a different port:
  uvicorn app:app --port 8080 --reload

- Database locked (SQLite): If multiple processes concurrently write, you may see SQLITE_BUSY. Try:
  - Ensure only one process writes at a time.
  - Retry the operation.
  - For development, deleting academic.db and starting fresh is acceptable (note: migrations will need to be re-applied).

- Missing migrations or endpoints returning 404 / errors:
  - Check GET /migrations to see applied steps.
  - Apply migrations in order using POST /migrate.

- Smoke endpoint import error (module not found):
  - Ensure the smoke test script is named smoke_test.py if api.py imports smoke_test.
  - Make sure your PYTHONPATH includes the project root so imports like `from domain import entities` work.

- Foreign key failures on enrollment/teaching creation:
  - Ensure referred student/course/teacher rows exist before creating the relationship.
  - Migrations must be applied so the FK constraints exist (apply step 4 before creating enrollments).

Recommended requirements.txt
Use this when creating environments:

fastapi
uvicorn[standard]
sqlalchemy
pydantic
streamlit
aiosqlite

Advanced notes & recommended improvements
- For production use, consider replacing SQLite with PostgreSQL for concurrency and robustness.
- Using Alembic (with SQLAlchemy ORM) for more advanced migrations is recommended for larger projects. This demo uses a self-contained MigrationService to illustrate in-process, zero-downtime evolution.
- Add integration tests around the HTTP API (e.g., pytest + httpx) to supplement the direct-service smoke test.
- Consider packaging the app with a proper entrypoint module (app.py) that constructs the FastAPI instance and avoids naming conflicts with smoke test script.

Appendix — example end-to-end sequence (commands)
1. Start server (adjust module name as needed):
   uvicorn app:app --reload

2. Apply step 1:
   curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":1}'

3. Create a student (no email yet):
   curl -X POST "http://127.0.0.1:8000/students" -H "Content-Type: application/json" -d '{}'

4. Apply step 2 (add email):
   curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":2}'

5. Update student to add email:
   curl -X PUT "http://127.0.0.1:8000/students/1" -H "Content-Type: application/json" -d '{"email":"alice@example.com"}'

6. Apply step 3 (courses):
   curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":3}'

7. Create course:
   curl -X POST "http://127.0.0.1:8000/courses" -H "Content-Type: application/json" -d '{"level":"Undergrad"}'

8. Apply step 4 (enrollments):
   curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":4}'

9. Create enrollment:
   curl -X POST "http://127.0.0.1:8000/enrollments" -H "Content-Type: application/json" -d '{"student_id":1,"course_id":1}'

10. Apply step 5 (teachers) and create teacher:
    curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":5}'
    curl -X POST "http://127.0.0.1:8000/teachers" -H "Content-Type: application/json" -d '{}'

11. Apply step 6 (teachings) and create a teaching:
    curl -X POST "http://127.0.0.1:8000/migrate" -H "Content-Type: application/json" -d '{"step":6}'
    curl -X POST "http://127.0.0.1:8000/teachings" -H "Content-Type: application/json" -d '{"teacher_id":1,"course_id":1}'

12. Run smoke test:
    - Via API: curl -X POST "http://127.0.0.1:8000/smoke"
    - Or locally: python main.py  (or python smoke_test.py depending on file name)

If you follow this manual and the provided code, you should be able to run the system, evolve schema without restarting, and exercise the full CRUD surface and relationships.

If you want, I can also:
- Provide a ready-to-use app.py FastAPI entrypoint (ensuring names don't conflict).
- Produce a requirements.txt or a Dockerfile to containerize the service.
- Add a small script to run the migrations 1..6 automatically and then start the server.

Contact the product team at ChatDev for feature requests, production hardening and integrations.