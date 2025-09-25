# Academic Management System — User Manual

Version: initial (FastAPI backend + Streamlit minimal UI)  
Designed for: Python 3.11

This project is an academic management system that manages Students, Courses, and Teachers and their many-to-many relationships (Enrollments and Teachings). It follows a lightweight Domain-Driven Design (entities, repositories, services) and uses SQLite for persistence with a simple zero-downtime migration runner.

This manual explains:
- What the system does
- Architecture & file layout
- Installation and setup
- How to run the API and Streamlit UI
- Migration workflow (adding SQL migrations)
- API reference with examples (CRUD + relationship endpoints)
- Troubleshooting, limitations, and recommended next steps

---

Table of contents
- What it does (Quick overview)
- Project structure (important files)
- Prerequisites
- Installation
- Running the application
- API (endpoints, example requests/responses)
- Streamlit UI (usage)
- Migrations (how the runner works and how to add migrations)
- Development notes (changing DB, concurrency, tests)
- Troubleshooting & FAQs
- Limitations & recommended improvements

---

What it does (Quick overview)
- Manages three domain entities:
  - Student: id (int PK), name (string), email (string, unique)
  - Course: id (int PK), title (string), level (string)
  - Teacher: id (int PK), name (string), department (string)
- Relationships:
  - Enrollment: many-to-many between Student and Course (explicit enrollments table)
  - Teaching: many-to-many between Teacher and Course (explicit teachings table)
- Provides CRUD APIs for Students, Courses, Teachers
- Provides endpoints to list/create/delete enrollments and teachings
- Uses SQLAlchemy ORM models, Pydantic schemas, a repository layer, and a service layer
- Minimal Streamlit UI for inspection and simple operations (create/list/enroll/assign)

---

Project structure (high-level)
- main.py — FastAPI app entrypoint; runs migrations on startup and includes the router
- db.py — SQLAlchemy engine, Base, session factory, get_db dependency
- migrations.py — simple SQL migrations runner that tracks migrations in a migrations table
- migrations/0001_create_tables.sql — initial schema
- models.py — SQLAlchemy ORM models and association tables
- schemas.py — Pydantic request/response models
- repositories.py — repository layer (DB access, simple SQL for associations)
- services.py — business logic layer (validation, orchestration)
- api.py — FastAPI router exposing endpoints under /api
- streamlit_ui.py — minimal Streamlit frontend used to inspect and interact
- requirements.txt — pinned dependencies
- readme.md — quick-start guide (also included in repo)

---

Prerequisites
- Python 3.11
- pip
- (Optional) Virtual environment tool: venv / virtualenv / conda

---

Installation (local dev)
1. Clone repository and cd into project directory.
2. Create and activate a Python 3.11 virtual environment:
   - Unix/macOS:
     - python3.11 -m venv .venv
     - source .venv/bin/activate
   - Windows (PowerShell):
     - python -m venv .venv
     - .\.venv\Scripts\Activate.ps1
3. Install dependencies:
   - pip install -r requirements.txt

Notes:
- The current requirements contain versions tested with Python 3.11:
  - fastapi, uvicorn, SQLAlchemy, pydantic, streamlit, requests

---

Run the app (development)
1. Start the API server:
   - uvicorn main:app --reload
   - By default the API root is at: http://127.0.0.1:8000/api
   - Open automatic docs: http://127.0.0.1:8000/docs
2. On first startup, migrations are run automatically and the SQLite DB file academic.db is created in the project root.
3. Run the Streamlit UI in a second terminal:
   - streamlit run streamlit_ui.py
   - Streamlit UI default: opens at http://localhost:8501

Important concurrency note (SQLite):
- SQLite has limitations for high-concurrency multi-process servers. For dev, uvicorn --reload is fine. For production use, consider using PostgreSQL or a single-process server with proper connection handling.

---

API reference (base URL: http://127.0.0.1:8000/api)

Common headers:
- Content-Type: application/json

Student endpoints
- Create student
  - POST /api/students
  - Body:
    {
      "name": "Alice Smith",
      "email": "alice@example.com"
    }
  - Success: 201 Created returns created Student (id, name, email)
  - Error: 400 on duplicate email

- List students
  - GET /api/students?skip=0&limit=100
  - Returns: [ {id, name, email}, ... ]

- Get student
  - GET /api/students/{student_id}
  - Returns student or 404

- Update student
  - PUT /api/students/{student_id}
  - Body (partial):
    {
      "name": "New Name"
    }
  - Returns updated student or 404 / 400

- Delete student
  - DELETE /api/students/{student_id}
  - 204 No Content on success

Course endpoints
- Create course
  - POST /api/courses
  - Body:
    {
      "title": "Introduction to Programming",
      "level": "Undergraduate"
    }
  - Returns created course (id, title, level)

- List courses
  - GET /api/courses

- Get course
  - GET /api/courses/{course_id}

- Update course
  - PUT /api/courses/{course_id}

- Delete course
  - DELETE /api/courses/{course_id}

Teacher endpoints
- Create teacher
  - POST /api/teachers
  - Body:
    {
      "name": "Dr. John Doe",
      "department": "Computer Science"
    }

- List / Get / Update / Delete similar to Students/Courses

Enrollment endpoints (Student <-> Course)
- List enrollments
  - GET /api/enrollments
  - Returns: [ { "student_id": X, "course_id": Y }, ... ]

- Create enrollment (enroll student in course)
  - POST /api/enrollments
  - Body:
    {
      "student_id": 1,
      "course_id": 2
    }
  - 201 on success
  - Errors:
    - 404 if student or course not found
    - 400 if enrollment already exists

- Delete enrollment (unenroll)
  - DELETE /api/enrollments
  - Body:
    {
      "student_id": 1,
      "course_id": 2
    }
  - 204 No Content

Teaching endpoints (Teacher <-> Course)
- List teachings
  - GET /api/teachings

- Create teaching (assign teacher to course)
  - POST /api/teachings
  - Body:
    {
      "teacher_id": 1,
      "course_id": 2
    }

- Delete teaching (unassign)
  - DELETE /api/teachings
  - Body:
    {
      "teacher_id": 1,
      "course_id": 2
    }

Example curl flows
- Create a student:
  curl -s -X POST http://127.0.0.1:8000/api/students -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'

- Create course:
  curl -s -X POST http://127.0.0.1:8000/api/courses -H "Content-Type: application/json" -d '{"title":"Intro to Prog","level":"Undergraduate"}'

- Enroll student 1 in course 1:
  curl -s -X POST http://127.0.0.1:8000/api/enrollments -H "Content-Type: application/json" -d '{"student_id":1,"course_id":1}'

- List enrollments:
  curl -s http://127.0.0.1:8000/api/enrollments

Sample API response for a Student (JSON)
{
  "id": 1,
  "name": "Alice Smith",
  "email": "alice@example.com"
}

---

Streamlit UI (minimal)
- Purpose: quick inspection and basic interactions (create Student/Course/Teacher, enroll, assign).
- Start it:
  - streamlit run streamlit_ui.py
- What you can do:
  - See lists of Students, Courses, Teachers
  - Create Students / Courses / Teachers via simple forms
  - Enroll students into courses (via dropdowns)
  - Assign teachers to courses
- Notes:
  - Streamlit UI calls the API at http://localhost:8000/api — ensure API is running
  - For convenience the project allows CORS from all origins (development-focused)

---

Migrations (zero-downtime migration runner)
- migrations.py is a simple runner that:
  - Connects to academic.db (SQLite) directly
  - Ensures a migrations table exists:
    migrations (id, filename, applied_at)
  - Applies any .sql files in the migrations/ directory (lexically sorted) that have not yet been applied
  - Records applied migration filenames to prevent reapplying
- Adding a migration:
  1. Add a new SQL file to migrations/, e.g. 0002_add_description_to_courses.sql
  2. Put valid SQL statements in it (use CREATE TABLE IF NOT EXISTS / ALTER TABLE as required)
  3. Restart the FastAPI server; run_migrations() executes on startup and will apply new migrations
- Zero-downtime note:
  - This runner applies migrations at app startup. For small schema changes and low-traffic environments, it is effective.
  - For production environments, use a more robust migration tool (Alembic) and a deployment strategy that supports rolling upgrades and backward-compatible migrations.
- Rollback:
  - The runner does not provide automatic rollback; if a migration fails you must fix the migration.sql and re-run (or restore DB backup)
- Where migration files live:
  - migrations/*.sql

---

Development notes & configuration
- Database file:
  - academic.db is created in the project root. Change DATABASE_URL in db.py if you want a different file or a server DB.
- Switching DB engines:
  - Update DATABASE_URL in db.py and adjust create_engine args accordingly (SQLite uses connect_args={"check_same_thread": False})
  - For production, use PostgreSQL or MySQL rather than SQLite
- Concurrency / Uvicorn workers:
  - SQLite + multiple processes can cause database locking / file contention. If you use uvicorn with multiple workers, prefer a server DB or use a single worker.
- Module boundaries:
  - models.py — ORM + association tables
  - repositories.py — repository abstraction for CRUD + association raw SQL
  - services.py — business logic, validation, orchestration
  - api.py — endpoints and HTTP translation of service responses/exceptions
  - This separation helps maintain the domain modeling and supports incremental evolution

---

Testing (manual)
- No test suite included in this initial package. Quick test flow:
  1. Start API
  2. Create a student, course, teacher via POST endpoints or Streamlit UI
  3. Enroll and assign via endpoints
  4. Verify GET endpoints reflect changes

Automated testing recommendations:
- Add pytest-based unit tests:
  - Service-level tests (mock repositories)
  - Repository-level tests with a temporary SQLite DB (in-memory with sqlite:///:memory:)
  - API integration tests using TestClient from fastapi.testclient

---

Troubleshooting & FAQs
- Q: "I get IntegrityError when creating a student with an email that already exists."
  - A: Email is unique. Use a distinct email or handle the 400 response.

- Q: "Migrations did not run / new .sql did not apply."
  - A: Confirm the .sql filename is lexically after previously applied ones and present in migrations/ directory; check application stdout for "Applying migration: <name>" or errors printed by run_migrations(). The migrations runner records applied filenames in the migrations table.

- Q: "SQLite locking or OperationalError when multiple writes occur."
  - A: SQLite is not ideal for heavy concurrent writes. For production, move to PostgreSQL and configure SQLAlchemy accordingly.

- Q: "I want to reset the DB and start fresh."
  - A: Stop the server, delete academic.db and restart; the initial migration 0001_create_tables.sql will recreate tables. Also delete the migrations table if you want to reapply migrations from scratch (or delete the DB entirely).

- Q: "How to change DB location or use env var?"
  - A: Edit db.py DATABASE_URL constant or refactor to read from an environment variable (recommended for deployment).

- Q: "Why are association operations using raw SQL?"
  - A: Simpler handling of composite primary keys and to keep the repository layer straightforward. You can extend to SQLAlchemy ORM expressions if desired.

---

Limitations & recommended next steps
- Current limitations:
  - SQLite for persistence (not suitable for high-concurrency production)
  - Simple migration runner (no versioned down migrations, no branching)
  - No authentication/authorization
  - Minimal validation beyond basic schemas (no phone numbers, etc.)
  - No unit/integration tests included
  - Streamlit UI is minimal (inspection-only)

- Recommended next steps:
  - Introduce Alembic for robust migrations and version control of schema migrations
  - Swap SQLite for PostgreSQL for production deployments
  - Add authentication & role-based access control (admins, teachers, students)
  - Add more domain services (course enrollment rules, maximum capacity, prerequisites)
  - Add tests and CI pipeline
  - Add OpenAPI documentation comments and sample responses
  - Improve Streamlit UI or build a React/Next frontend for production usage

---

Appendix — Quick examples

Create student (curl)
curl -X POST http://127.0.0.1:8000/api/students -H "Content-Type: application/json" -d '{"name":"Alice","email":"alice@example.com"}'

Create course
curl -X POST http://127.0.0.1:8000/api/courses -H "Content-Type: application/json" -d '{"title":"Algorithms","level":"Undergraduate"}'

Enroll student (id 1) into course (id 1)
curl -X POST http://127.0.0.1:8000/api/enrollments -H "Content-Type: application/json" -d '{"student_id":1,"course_id":1}'

List enrollments
curl http://127.0.0.1:8000/api/enrollments

Assign teacher (id 1) to course (id 1)
curl -X POST http://127.0.0.1:8000/api/teachings -H "Content-Type: application/json" -d '{"teacher_id":1,"course_id":1}'

---

Contact / support
- For development help inside the project team: follow internal procedures (code review, pair programming)
- For production deployments or migration help: consider consulting a backend/infrastructure engineer to adapt DB, migration tooling, and deployment strategy.

---

Acknowledgements
- This project was built with FastAPI, SQLAlchemy, Pydantic, and Streamlit. The repository/service structure is intentionally simple but intended to be extended following Domain-Driven Design principles.

End of manual.