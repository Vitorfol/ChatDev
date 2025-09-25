manual.md

# Academic Management System — User Manual

Version: 1.0  
Language: Python 3.11  
Web framework: FastAPI  
ORM: SQLAlchemy  
Validation: Pydantic  
Persistence: SQLite (academic.db)  
UI: Minimal Streamlit inspector  
Purpose: a small domain-driven academic management backend that evolves incrementally via in-process migrations (zero‑downtime style). Includes a small automated smoke test.

This manual explains what the system provides, how to install and run it, how to operate incremental migrations, how to use the HTTP API and Streamlit UI, how to run the smoke test, and how to extend the system (add migrations).

Table of contents
- What this system does (high level)
- Project layout (files & responsibilities)
- Quick install (dependencies)
- Starting the API server (FastAPI / uvicorn)
- Applying schema evolution (migrations)
- Using the HTTP API (endpoints & examples)
- Streamlit minimal UI
- Running the automated smoke test
- Resetting / inspecting the DB
- Adding new migrations (how-to)
- Design notes (DDD, semantics and zero-downtime)
- Troubleshooting & FAQs
- Appendix: Example curl commands

---

What this system does (high level)
- Implements an academic domain with these entities and relationships:
  1. Student (id int PK; email added in migration step 2)
  2. Course (id int PK; level string)
  3. Enrollment (association Student ↔ Course)
  4. Teacher (id int PK)
  5. Teaching (association Teacher ↔ Course)
- Exposes CRUD endpoints (FastAPI) for Students, Courses, Enrollments, Teachers, Teachings.
- Uses an in-process MigrationManager (migrations.py) with incremental, idempotent migrations applied via an endpoint (/migrations/apply_next). The server does not need to be restarted to evolve schema in the provided workflow.
- A minimal Streamlit UI (streamlit_app.py) can call the API to inspect records and trigger "apply next migration".
- A smoke test (main.py) exercises the full migration sequence and basic CRUD operations to assert the system correctness.

Project layout (files & responsibilities)
- app.py — FastAPI app instance, wires router, ensures migration bookkeeping at startup.
- api.py — APIRouter, endpoint definitions for all entities and for applying migrations.
- db.py — SQLAlchemy engine, SessionLocal, declarative Base.
- models.py — SQLAlchemy ORM models (final schema), Pydantic request/response schemas.
- repositories.py — Repository layer: atomic DB operations per aggregate (StudentRepository, CourseRepository, ...).
- services.py — Service layer: business operations exposed to API and coordinating repositories.
- migrations.py — MigrationManager: idempotent, sequential migrations; tracks applied version in schema_versions table; exposes apply_next() method.
- main.py — Automated smoke test that applies migrations and performs CRUD checks with FastAPI TestClient.
- streamlit_app.py — Minimal Streamlit UI that lists records and can trigger apply_next migration.
- requirements.txt — Python dependencies to install.
- academic.db — SQLite DB file (created on first run).

Quick install (dependencies)
1. Create a Python 3.11 virtual environment (recommended)
   - python3.11 -m venv .venv
   - source .venv/bin/activate  (macOS/Linux)
   - .venv\Scripts\activate     (Windows PowerShell/CMD)

2. Install requirements
   - pip install --upgrade pip
   - pip install -r requirements.txt

requirements.txt includes:
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- streamlit
- requests

Starting the API server (FastAPI / uvicorn)
1. Start the application:
   - uvicorn app:app --reload --host 0.0.0.0 --port 8000

2. What happens at startup:
   - app.py registers the API router and calls migration_manager.ensure_version_table() (idempotent) to ensure schema_versions exists so migrations can be applied incrementally.

Applying schema evolution (migrations)
- The system stores migration state in a single-row table schema_versions (integer). Each migration is a Python function (in migrations.py) applied sequentially.
- To apply the next migration without restarting:
  - POST /migrations/apply_next
  - GET /migrations/version returns current version and total migrations

Migrations sequence (6 steps implemented)
1. migration_1_create_students_id
   - Create students table with id INTEGER PRIMARY KEY
2. migration_2_add_student_email
   - Add email column to students (TEXT). Implemented carefully to be idempotent on SQLite using PRAGMA table_info.
3. migration_3_create_courses
   - Create courses table with id (PK) and level (TEXT).
4. migration_4_create_enrollments_association
   - Create enrollments table with id, student_id, course_id, foreign keys, and a unique index to prevent duplicate pairs.
5. migration_5_create_teachers
   - Create teachers table with id (PK).
6. migration_6_create_teachings_association
   - Create teachings table with id, teacher_id, course_id, foreign keys, and a unique index.

Tips:
- Use POST /migrations/apply_next repeatedly to progress through steps one-by-one.
- The Streamlit UI includes an "Apply Next Migration" button for convenience.

Using the HTTP API (endpoints & examples)
Base URL (default when running uvicorn): http://localhost:8000

Important endpoints:
- Migrations
  - POST /migrations/apply_next — apply the next migration step
  - GET /migrations/version — returns {"version": n, "total_migrations": 6}

- Students
  - POST /students  (body: {"id": int, "email": str?})
  - GET /students
  - GET /students/{student_id}
  - PUT /students/{student_id}  (body: {"email": str?})
  - DELETE /students/{student_id}

- Courses
  - POST /courses (body: {"id": int, "level": str?})
  - GET /courses
  - GET /courses/{course_id}
  - PUT /courses/{course_id} (body: {"level": str?})
  - DELETE /courses/{course_id}

- Enrollments
  - POST /enrollments (body: {"student_id": int, "course_id": int})
  - GET /enrollments
  - GET /enrollments/{enrollment_id}
  - DELETE /enrollments/{enrollment_id}

- Teachers
  - POST /teachers (body: {"id": int})
  - GET /teachers
  - GET /teachers/{teacher_id}
  - DELETE /teachers/{teacher_id}

- Teachings
  - POST /teachings (body: {"teacher_id": int, "course_id": int})
  - GET /teachings
  - GET /teachings/{teaching_id}
  - DELETE /teachings/{teaching_id}

Example curl flows
- Apply next migration:
  - curl -X POST http://localhost:8000/migrations/apply_next
- Create a student (after students table exists):
  - curl -X POST http://localhost:8000/students -H "Content-Type: application/json" -d '{"id":1,"email":"alice@example.com"}'
- Create a course:
  - curl -X POST http://localhost:8000/courses -H "Content-Type: application/json" -d '{"id":10,"level":"101"}'
- Create an enrollment (after enrollments table exists):
  - curl -X POST http://localhost:8000/enrollments -H "Content-Type: application/json" -d '{"student_id":1,"course_id":10}'

Notes:
- The API uses Pydantic models for validation and SQLAlchemy ORM for storage.
- The server code uses domain-driven design separation: API -> Services -> Repositories -> DB.

Streamlit minimal UI
- Run:
  - streamlit run streamlit_app.py
- By default, Streamlit tries to fetch API from st.secrets["api_base"] or "http://localhost:8000".
- The UI shows lists of Students, Courses, Teachers, Enrollments, Teachings and provides a button to trigger "Apply Next Migration".
- Use it for quick inspection and to drive migrations interactively.

Running the automated smoke test
- The repository includes main.py — an automated smoke test that:
  - Ensures the schema_versions table exists.
  - Calls POST /migrations/apply_next repeatedly to apply all defined migrations.
  - Runs CRUD tests (create/get/update/delete) for students, courses, enrollments, teachers, and teachings.
- Run:
  - python main.py
- Expected output:
  - "SMOKE TEST PASSED" on success.
  - On assertion failure the script prints "SMOKE TEST FAILED:" and exits with non-zero status.
- Note: main.py uses fastapi.testclient to exercise endpoints without needing a separate running server, but app import expects the modules to be importable and initialized. If you prefer to run against a running server, you can rework the script to use requests against the running server.

Resetting / inspecting the DB
- DB file location: ./academic.db (sqlite file created by SQLAlchemy engine)
- Quick reset:
  - Stop the server and delete academic.db, then restart. (This is the simplest development reset.)
  - Alternatively, you can interactively drop/clean tables using SQL; but deleting academic.db yields a clean slate quickly.
- The migration manager will create schema_versions table and then migrations are applied from version 0 upward.

Adding new migrations (how-to)
1. Open migrations.py.
2. Create a new migration method (e.g., migration_7_add_something) with a docstring describing semantics.
3. Append the function to MigrationManager.migrations list in the order you want it applied.
4. Implement idempotent DDL (CREATE TABLE IF NOT EXISTS, ALTER TABLE only when safe, or check PRAGMA table_info for columns).
5. Deploy; call POST /migrations/apply_next to apply the next migration.

Design notes (DDD, semantics and zero-downtime)
- Domain Driven Design separation:
  - models.py contains domain entities (ORM and Pydantic) preserving entity names and docstrings across evolution.
  - repositories.py encapsulates DB access and error handling.
  - services.py contains business logic, transaction boundaries and is the interface used by api.py.
  - api.py maps the domain services to HTTP endpoints.
- Semantics preserved:
  - Entity names, attribute names and docstrings are preserved across migrations so the vocabulary remains stable.
- Zero‑downtime style:
  - Migrations are applied in-process via the /migrations/apply_next endpoint.
  - Migrations are idempotent and careful about visibility: migrations.ensure_version_table uses explicit transactions and re-queries to avoid stale visibility.
  - The server need not be restarted to evolve the schema in this workflow (useful for small deployments and demo environments). For production, consider using a tested migration tool (Alembic), comprehensive schema change practices, and careful rolling upgrade strategy.

Troubleshooting & FAQs
Q: The Smoke test fails with OperationalError complaining about a missing table.
A: Ensure you applied required migrations (call POST /migrations/apply_next until it responds "No more migrations."). The smoke test main.py calls the migration manager itself when run as a TestClient, but if you run the server separately you must call apply_next repeatedly (or run main.py).

Q: Streamlit shows connection errors or times out.
A: Ensure the FastAPI server is running at the address configured in st.secrets["api_base"] or default http://localhost:8000. If running Streamlit on another host or container, set the API_BASE secret or replace the default in streamlit_app.py accordingly.

Q: SQLite concurrency / check_same_thread error.
A: db.py config sets connect_args={"check_same_thread": False} which is suitable for small dev setups. For heavier production loads, switch to a proper DB server (Postgres) and a robust migration strategy (Alembic, zero-downtime migrations coordinated during deploys).

Q: How to view the raw DB contents?
A: Use sqlite3 CLI: sqlite3 academic.db
   - sqlite> .tables
   - sqlite> SELECT * FROM students;

Q: How to reset version to re-run migrations from scratch?
A:
   - Option A (development): stop server, delete academic.db, restart, then call apply_next repeatedly.
   - Option B (careful): open academic.db and set schema_versions.version=0 (or delete rows) — not recommended unless you know the exact migration state.

Extending the domain / code conventions
- Preserve existing entity names and docstrings to keep the vocabulary (living ontology).
- Add new migrations as idempotent functions; append to migrations list in migrations.py.
- Repositories/services should remain stable; add new methods as needed.

Appendix: Example curl commands (quick reference)
- Apply next migration:
  - curl -X POST http://localhost:8000/migrations/apply_next
- View migration version:
  - curl http://localhost:8000/migrations/version
- Create Student:
  - curl -X POST http://localhost:8000/students -H "Content-Type: application/json" -d '{"id":1,"email":"alice@example.com"}'
- Get Student:
  - curl http://localhost:8000/students/1
- Update Student:
  - curl -X PUT http://localhost:8000/students/1 -H "Content-Type: application/json" -d '{"email":"new@example.com"}'
- Create Course:
  - curl -X POST http://localhost:8000/courses -H "Content-Type: application/json" -d '{"id":10,"level":"101"}'
- Create Enrollment:
  - curl -X POST http://localhost:8000/enrollments -H "Content-Type: application/json" -d '{"student_id":1,"course_id":10}'
- Create Teacher:
  - curl -X POST http://localhost:8000/teachers -H "Content-Type: application/json" -d '{"id":900}'
- Create Teaching:
  - curl -X POST http://localhost:8000/teachings -H "Content-Type: application/json" -d '{"teacher_id":900,"course_id":10}'

Final notes
- This system is designed for demonstration and incremental evolution in development or small deployments.
- For production-grade migration and scaling, adopt Alembic (or your DB migration tool), transactional schema evolution best practices, a production DB (Postgres), and CI/CD that runs DB migrations in a controlled way.
- If you need assistance converting this pattern to Alembic, deploying to a container or cloud run environment, or expanding the domain model, contact the development team.

Contact / Support
- For product/feature questions, architectural guidance or priority feature requests, contact the product owner (Chief Product Officer) and the engineering team.