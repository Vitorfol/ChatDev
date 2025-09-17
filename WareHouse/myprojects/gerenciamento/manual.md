# School Management — User Manual

A simple microfrontend web application for basic school management.  
Built with Python (Flask) backend and plain HTML/CSS/vanilla JS microfrontends (loaded in iframes).  
Use it to register students and teachers, create classes with schedules, and create relationships:
- assign teachers to students
- assign students and teachers to classes

Contents
- Features overview
- Quick prerequisites
- Install & run (local)
- File layout (what each file does)
- UI guide — how to use the app
- API reference (endpoints + sample payloads)
- Data storage details
- Troubleshooting & tips
- Development & extension notes (Docker, improvements, security)

---

## Features overview

- Microfrontend shell that hosts three microfrontends:
  - Students — register students, list students, assign teachers, assign to classes
  - Teachers — register teachers, list teachers
  - Classes — create classes with schedules, list classes, assign teacher to class
- Storage: simple JSON file persisted on disk (data/db.json)
- Lightweight, clean HTML/CSS UI with straightforward interaction patterns
- REST API for all operations (create/list and relationship endpoints)

---

## Quick prerequisites

- Python 3.8+ (tested with 3.8/3.9/3.10)
- pip (Python package manager)
- (Optional) Git (to clone repository)

No heavy frontend build step is required — plain HTML/CSS/JS.

---

## Install & run (local)

1. Clone or place the project files in a directory
   - Files required (examples from repository):
     - main.py, storage.py, models.py
     - templates: index.html, micro_students.html, micro_teachers.html, micro_classes.html
     - static/: css/style.css, js/micro_students.js, js/micro_teachers.js, js/micro_classes.js
     - (optional) data/db.json (the app will create it automatically if missing)

2. Create and activate a virtual environment (recommended)
   - macOS / Linux:
     ```
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Windows (PowerShell):
     ```
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. Install dependencies
   - The app uses Flask. Install it:
     ```
     pip install Flask
     ```
   - (Optional) pin versions by creating requirements.txt:
     ```
     Flask>=2.0
     ```

4. Ensure the data directory exists
   - The app will create the required data directory and file automatically. If you want deterministic starting state, include the provided data/db.json.

5. Run the app
   ```
   python main.py
   ```
   - By default it runs Flask on http://127.0.0.1:5000 in debug mode (as configured).
   - If you want to run on a different host/port or turn off debug, edit the final block in main.py (app.run(...)) or set FLASK_APP/FLASK_ENV as desired.

6. Open the UI
   - Navigate to http://127.0.0.1:5000 in your browser.

---

## File layout and responsibilities

- main.py
  - Flask web server, route handlers for:
    - UI routes: "/", "/micro/students", "/micro/teachers", "/micro/classes"
    - API endpoints (GET/POST for students, teachers, classes)
    - Relationship endpoints for assignments
  - Serves static files and templates.

- storage.py
  - JSON-backed storage layer using a file (default: data/db.json).
  - Thread-safe read/write using threading.Lock.
  - Methods for creating/listing entities and for assigning relationships:
    - create_student, get_all_students
    - create_teacher, get_all_teachers
    - create_class, get_all_classes
    - assign_teacher_to_student, assign_student_to_class, assign_teacher_to_class

- models.py
  - Domain models: Student, Teacher, ClassRoom (dataclasses).
  - to_dict / from_dict helpers for storage.

- templates/
  - index.html — shell that embeds microfrontends via iframes and provides tabs.
  - micro_students.html — students microfrontend.
  - micro_teachers.html — teachers microfrontend.
  - micro_classes.html — classes microfrontend.

- static/
  - css/style.css — application styling (clean, simple).
  - js/micro_students.js — JS logic for students microfrontend (fetching APIs, rendering, forms).
  - js/micro_teachers.js — JS logic for teachers microfrontend.
  - js/micro_classes.js — JS logic for classes microfrontend.

- data/db.json (optional)
  - JSON initial database (app creates it automatically if missing).

---

## UI guide — how to use the app

Open the shell page (/) — it contains three tabs: Students, Teachers, Classes. Tabs switch between microfrontends (each loaded in an iframe).

1. Students microfrontend
   - Register Student
     - Fill Name (required), Age (optional), Email (optional).
     - Click "Register Student".
     - After success, the student list updates.
   - Assign Teacher to Student
     - Select a student, select a teacher (teachers must exist first).
     - Click "Assign Teacher to Student".
   - Assign Student to Class
     - Select a student and a class (classes must exist).
     - Click "Assign Student to Class".
   - Students List
     - Displays registered students, shows IDs, age, email, lists assigned teacher IDs and class IDs.

2. Teachers microfrontend
   - Register Teacher
     - Fill Name (required), Subject, Email.
     - Click "Register Teacher".
   - Teachers List
     - Shows registered teachers with IDs and a list of student IDs assigned to them.

3. Classes microfrontend
   - Create Class
     - Provide class name (required).
     - Provide schedule as comma-separated items, example:
       - "Mon 10:00-11:00, Tue 09:00-10:00"
     - Click "Create Class".
   - Assign Teacher to Class
     - Select a teacher and a class.
     - Click "Assign Teacher to Class".
   - Classes List
     - Displays class name, ID, assigned teacher ID, and schedule lines.

Notes:
- After creating entities, other microfrontends will pick up lists on their next load or when creating new items (the microfrontends query the backend directly).
- IDs are numeric and auto-incremented by storage.

---

## API reference

All API endpoints are served from the same origin (no CORS required for the bundled UI). Use them for automation or integration.

Base path: http://127.0.0.1:5000

1. Students
- GET /api/students
  - Response: JSON array of student objects
  - Example:
    [
      { "id": 1, "name": "Alice", "age": 12, "email": "a@example.com", "teachers": [], "classes": [] },
      ...
    ]

- POST /api/students
  - Request JSON:
    {
      "name": "Alice",
      "age": 12,
      "email": "a@example.com"
    }
  - Response: 201 Created, created student JSON (with id)

2. Teachers
- GET /api/teachers
  - Response: JSON array of teacher objects

- POST /api/teachers
  - Request JSON:
    {
      "name": "Mr. Smith",
      "subject": "Math",
      "email": "smith@example.com"
    }
  - Response: 201 Created, created teacher JSON

3. Classes
- GET /api/classes
  - Response: JSON array of class objects

- POST /api/classes
  - Request JSON:
    {
      "name": "Math 101",
      "schedule": [
        {"day": "Mon", "time": "10:00-11:00"},
        {"day": "Tue", "time": "09:00-10:00"}
      ]
    }
  - Response: 201 Created, created class JSON

4. Relationship endpoints
- POST /api/assign_teacher_to_student
  - Request JSON: { "student_id": 1, "teacher_id": 2 }
  - Response: 200 OK on success or 400 with error message

- POST /api/assign_student_to_class
  - Request JSON: { "student_id": 1, "class_id": 3 }

- POST /api/assign_teacher_to_class
  - Request JSON: { "teacher_id": 2, "class_id": 3 }

Examples using curl:
- Create a student:
  ```
  curl -X POST -H "Content-Type: application/json" \
    -d '{"name":"Alice","age":12,"email":"a@x.com"}' \
    http://127.0.0.1:5000/api/students
  ```

- Assign teacher to student:
  ```
  curl -X POST -H "Content-Type: application/json" \
    -d '{"student_id":1,"teacher_id":2}' \
    http://127.0.0.1:5000/api/assign_teacher_to_student
  ```

---

## Data storage details

- Storage file: data/db.json (default, configurable in main.py by changing DB_FILE constant)
- File structure:
  ```
  {
    "next_ids": {"student": 1, "teacher": 1, "class": 1},
    "students": [...],
    "teachers": [...],
    "classes": [...]
  }
  ```
- Concurrency:
  - storage.py uses threading.Lock around file read/write to avoid concurrent corruption in the simple single-process server. This is adequate for this lightweight demo, but not for multi-process production servers (use a real DB for production).
- If the file is missing, the app will create and initialize it automatically.

---

## Troubleshooting & common issues

- "Port already in use" error when starting Flask:
  - Either stop the process using the port or change the port in main.py (app.run(..., port=XXXX)).

- Static files (CSS/JS) not loading:
  - Confirm static files are in static/css and static/js directories and the Flask app's static_folder is configured (default used).
  - Check browser console/network tab for 404s.

- Permission errors writing data/db.json:
  - Ensure the process has write permissions in the project directory. Adjust file permissions or run with appropriate user.

- Data not appearing in UI after actions:
  - Microfrontends call the API to reload lists. If they fail, check browser console for fetch errors; verify the backend is running and endpoints return 200.
  - If using different origin or host, cross-origin iframe issues may arise — for this demo everything is same origin.

- Corrupted db.json:
  - If db.json becomes invalid JSON, stop server and restore from backup or remove it to let the app recreate an initial empty database (existing data lost if you remove file).

---

## Development & extension notes

- Run with environment variables / different host:
  - Modify app.run(...) in main.py or change to use FLASK_APP/FLASK_ENV if using flask CLI.

- Docker (simple example)
  - Example Dockerfile:
    ```
    FROM python:3.10-slim
    WORKDIR /app
    COPY . /app
    RUN pip install --no-cache-dir Flask
    EXPOSE 5000
    CMD ["python", "main.py"]
    ```
  - Build and run:
    ```
    docker build -t school-microfrontend .
    docker run -p 5000:5000 -v $(pwd)/data:/app/data school-microfrontend
    ```
  - Mounting the data directory preserves db.json between container runs.

- Multi-microfrontend extension
  - Each microfrontend is an independent HTML page loaded inside an iframe by the shell.
  - To add another microfrontend:
    - Create template under templates/ and assets under static/.
    - Add a new tab button in templates/index.html and an iframe with src="/micro/<name>".
    - Add a new route in main.py to serve that template.

- Suggested improvements
  - Replace JSON file with an actual database (SQLite/Postgres) for concurrency and reliability.
  - Add input validation on the server for payloads.
  - Implement authentication/authorization for admin or per-role access.
  - Improve UI: searchable lists, display teacher/class names instead of IDs, better schedule picker.
  - Add server-side validation for schedule overlaps, required fields, and email formats.
  - Consider switching microfrontends to use a shared event bus or postMessage for tighter integration (instead of reloading via API calls).

---

## Security considerations

- This demo has no authentication and should not be exposed publicly in production.
- Data stored as plain JSON on disk — do not store sensitive PII in this demo.
- Avoid running in debug mode in production (Flask debug gives an interactive debugger).
- If exposing APIs externally, implement CSRF protections, rate limiting and authentication.

---

## Example usage flow (quick walkthrough)

1. Start server:
   ```
   python main.py
   ```

2. Open http://127.0.0.1:5000

3. Add a teacher:
   - Switch to Teachers tab
   - Register "Ms. Jane", subject "English"

4. Add a class:
   - Switch to Classes tab
   - Create "English 7A" with schedule "Mon 09:00-10:00, Wed 09:00-10:00"

5. Assign teacher to class:
   - In Classes tab, choose Ms. Jane and English 7A, click assign

6. Add a student:
   - Switch to Students tab
   - Register "Tim", age 13

7. Assign teacher to student:
   - In Students tab, choose Tim and Ms. Jane, click assign

8. Add student to class:
   - In Students tab, choose Tim and English 7A, click assign

9. Verify:
   - Look at students list, teachers list, classes list to confirm the relationships appear (IDs are shown, schedule lines shown in classes).

---

If you want, I can:
- Provide a ready-to-run requirements.txt or pyproject.toml.
- Create a Docker Compose configuration for local development (with volume for data).
- Add a small script that seeds sample data for demo purposes.