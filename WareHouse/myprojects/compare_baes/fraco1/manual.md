# Education Manager API — User Manual

A lightweight FastAPI-based service to manage Students, Courses, and Teachers with SQLite persistence.

Core features
- CRUD endpoints for Student, Course, and Teacher entities.
- Student has email (unique) and may be enrolled in many Courses (many-to-many).
- Course has title and level (beginner/intermediate/advanced) and may be assigned to a Teacher (one-to-many).
- Teacher may have many Courses; deleting a Teacher sets associated Course.teacher_id to null (DB-level ON DELETE SET NULL).
- SQLite persistence (./app.db). Tables are created automatically on startup.
- OpenAPI docs available at /docs (Swagger UI) and /redoc.

Contents
- Quick start (install & run)
- Database notes & reset
- Endpoints (requests & example payloads)
- Validation and business rules
- Example usage (curl + Python requests)
- Running in Docker
- Troubleshooting & development tips
- Production guidance & security notes

Quick start

1) Prerequisites
- Python 3.9+ (3.10/3.11 recommended)
- Git (optional)
- Recommended: virtual environment (venv/venvwrapper/conda)

2) Clone repository (or place files into a project directory)
git clone <your-repo-url>
cd <repo-directory>

3) Create and activate virtual environment
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

4) Install dependencies
pip install -r requirements.txt

5) Run the app (development)
uvicorn main:app --reload

- The server will create SQLite tables automatically on startup.
- Default address: http://127.0.0.1:8000
- Swagger UI (interactive API docs): http://127.0.0.1:8000/docs
- Redoc: http://127.0.0.1:8000/redoc
- Health check endpoint: GET /__health__

Database & persistence

- SQLite file: ./app.db (relative to project root)
- If you need to reset the database in development, stop the server and remove app.db:
  rm ./app.db
  Then restart uvicorn to recreate tables.
- The SQLAlchemy models live in models.py and the DB engine is configured in database.py. SQLite foreign keys enforcement is enabled via PRAGMA on connection.

API endpoints (summary)

Base URL: http://127.0.0.1:8000

Students
- POST /students/
  - Create a new student.
  - Request body (JSON):
    {
      "name": "Alice Example",
      "email": "alice@example.com"
    }
  - Response: StudentRead with courses list (empty by default).
  - Validation: email must be unique; email validated by Pydantic EmailStr.

- GET /students/?skip=0&limit=100
  - List students (pagination with skip & limit).
  - Response: list[StudentRead]

- GET /students/{student_id}
  - Retrieve single student (includes enrolled courses).

- PUT /students/{student_id}
  - Update a student (partial updates supported).
  - Request body (JSON): include only fields you want to change
    {
      "name": "Alice Newname",
      "email": "newalice@example.com"
    }
  - Email uniqueness enforced if provided.

- DELETE /students/{student_id}
  - Delete a student. Response code: 204 No Content.

- POST /students/{student_id}/courses/{course_id}
  - Enroll the student in the course (adds many-to-many association).
  - Response: StudentRead (with updated courses list).

- DELETE /students/{student_id}/courses/{course_id}
  - Remove an enrollment. Response: StudentRead.

Courses
- POST /courses/
  - Create a course.
  - Request body example:
    {
      "title": "Intro to Python",
      "level": "Beginner",          # optional; normalization -> "beginner"
      "teacher_id": 1               # optional
    }
  - Response: CourseRead (students empty by default).
  - `level` will be normalized to lowercase and must be one of:
    - "beginner"
    - "intermediate"
    - "advanced"
  - If teacher_id is provided, teacher must exist.

- GET /courses/?skip=0&limit=100
  - List courses (pagination).

- GET /courses/{course_id}
  - Retrieve a course (includes enrolled students and teacher_id).

- PUT /courses/{course_id}
  - Update course fields; partial update supported (exclude_unset semantics):
    - If teacher_id is included in payload (even null), it will be applied.
    - If teacher_id is omitted, the existing assignment will be kept.
  - Example to unassign teacher:
    { "teacher_id": null }

- DELETE /courses/{course_id}
  - Delete course. Response code: 204 No Content.

Teachers
- POST /teachers/
  - Create a teacher.
  - Request body:
    {
      "name": "Dr. Smith",
      "email": "smith@example.com"
    }
  - Response: TeacherRead (courses list empty by default).

- GET /teachers/?skip=0&limit=100
  - List teachers.

- GET /teachers/{teacher_id}
  - Get teacher (includes courses list: CourseSimple items).

- PUT /teachers/{teacher_id}
  - Update teacher (partial).

- DELETE /teachers/{teacher_id}
  - Delete teacher. Database-level behavior: ON DELETE SET NULL on Course.teacher_id, so associated courses will remain but their teacher_id will be set to null. Response: 204 No Content.

Validation & business rules

- Student.email:
  - Type-checked via Pydantic EmailStr.
  - Must be unique. Creating/updating with email that duplicates another student returns 400.

- Course.level:
  - Optional. If provided it is normalized (trim + lowercase). Allowed values:
    - beginner
    - intermediate
    - advanced
  - Empty string or whitespace is treated as None.

- Partial updates:
  - PUT endpoints use Pydantic models that accept optional fields and the code uses exclude_unset semantics so omitted fields are not overwritten.

- Relationships:
  - Student <-> Course: many-to-many via association table student_courses.
  - Teacher -> Course: one-to-many using teacher_id FK, ondelete=SET NULL.

OpenAPI / Docs
- Interactive docs: /docs (Swagger UI) — useful for exploring endpoints and trying out requests.
- /redoc for alternate API docs.

Example usage

1) Create a teacher (curl)
curl -X POST "http://127.0.0.1:8000/teachers/" -H "Content-Type: application/json" -d '{
  "name": "Dr. Ada Lovelace",
  "email": "ada@school.edu"
}'

2) Create a course and assign teacher (curl)
curl -X POST "http://127.0.0.1:8000/courses/" -H "Content-Type: application/json" -d '{
  "title": "Algorithms 101",
  "level": "Intermediate",
  "teacher_id": 1
}'

3) Create a student
curl -X POST "http://127.0.0.1:8000/students/" -H "Content-Type: application/json" -d '{
  "name": "Bob Student",
  "email": "bob@student.edu"
}'

4) Enroll student in course
curl -X POST "http://127.0.0.1:8000/students/1/courses/1"

5) List students
curl "http://127.0.0.1:8000/students/"

6) Update course level
curl -X PUT "http://127.0.0.1:8000/courses/1" -H "Content-Type: application/json" -d '{"level":"advanced"}'

7) Unassign a course's teacher
curl -X PUT "http://127.0.0.1:8000/courses/1" -H "Content-Type: application/json" -d '{"teacher_id": null}'

Python requests example
from requests import post, get, put
base = "http://127.0.0.1:8000"
# create student
resp = post(f"{base}/students/", json={"name":"Charlie","email":"charlie@example.com"})
print(resp.status_code, resp.json())
# enroll
post(f"{base}/students/3/courses/1")

Error handling (common responses)
- 400 Bad Request: invalid payload or business rule violation (e.g., duplicate email, invalid level)
- 404 Not Found: entity id not present (student/course/teacher)
- 500 Internal Server Error: generic DB or unexpected exception (server will return error detail)

Health / Missing dependencies
- If required dependencies are not installed and the app is started, a lightweight app will respond with an error at / describing the missing module and suggesting pip install -r requirements.txt.
- /__health__ returns status info when dependencies are missing.

Running in Docker (example)

Dockerfile (example)
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

docker-compose.yml (example)
version: "3.8"
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./app.db:/app/app.db
    environment:
      - PYTHONUNBUFFERED=1

Notes:
- The above mounts app.db to persist SQLite outside the container.
- For production use, prefer a production-grade DB (Postgres) and proper migrations (Alembic).

Troubleshooting & tips

- If endpoints return 422 Unprocessable Entity, check payload types vs Pydantic schemas (email format, allowed level values).
- Duplicate email on student create/update -> 400 "Student with this email already exists".
- If you modify models.py: delete app.db (or run a migration tool) to recreate structure. The current code uses Base.metadata.create_all() — it won't alter columns in an existing DB.
- To view DB content directly, use sqlite3:
  sqlite3 ./app.db
  sqlite> .tables
  sqlite> SELECT * FROM students;
- If you see errors at import-time about missing packages, ensure your venv is activated and you ran pip install -r requirements.txt.
- Use /docs to test endpoints interactively.

Development notes

- Files of interest:
  - main.py — FastAPI app and endpoints
  - models.py — SQLAlchemy models and relationships
  - schemas.py — Pydantic request/response models and validation
  - crud.py — DB operations used by endpoints
  - database.py — engine/session and dependency injection
  - requirements.txt — pinned dependencies

- The app uses SQLAlchemy sessions via a dependency get_db() that yields a session. Sessions are closed automatically after request.

- The endpoints use object return and Pydantic orm_mode in response schemas, so SQLAlchemy model instances can be returned directly.

Security & production guidance

- Authentication/authorization: none provided. Add OAuth2/JWT/basic auth or proxy behind an API gateway for production.
- Use a robust RDBMS (Postgres) in production. Migrate to SQLAlchemy URL like postgresql+psycopg2://user:pass@host/db and manage migrations with Alembic.
- Do not serve debug data/logs in production. Configure proper logging, monitoring and error reporting.
- Consider connection pooling, max workers, and running with an ASGI server behind a reverse proxy (e.g., Uvicorn/ Gunicorn with workers or Hypercorn) for production load.

Testing checklist (basic)
- Create teacher, create course with teacher_id, create student, enroll student, verify student GET includes course.
- Update course level with allowed and disallowed values.
- Try to create two students with same email (expect 400).
- Delete teacher and confirm course.teacher_id becomes null.
- Delete student and confirm student removed and association row removed.

Contact / Support
- For product support or requests for enhancements (e.g., adding authentication, switching DB, adding paging metadata, or adding tests), contact the development team or open an issue in the project repository.

Appendix — Schema quick reference

StudentCreate / StudentRead:
- name: string
- email: string (Email)
- StudentRead includes id and courses (CourseSimple list)

CourseCreate / CourseRead:
- title: string
- level: optional string (beginner/intermediate/advanced)
- teacher_id: optional int
- CourseRead includes students (StudentSimple list)

TeacherCreate / TeacherRead:
- name: string
- email: optional email
- TeacherRead includes courses (CourseSimple list)

Final notes
This project is designed as a simple educational/demo API with sensible defaults and explicit behaviors around relationships and validation. It is intentionally small and readable so you can iterate, add authentication, swap databases, or add migrations as your needs grow.

If you want, I (product) can:
- provide a step-by-step tutorial notebook / small Tkinter client to exercise the API,
- add Docker Compose with Postgres and Alembic for a production-like environment,
- or draft an OpenAPI client for your front-end.

Which would you like next?