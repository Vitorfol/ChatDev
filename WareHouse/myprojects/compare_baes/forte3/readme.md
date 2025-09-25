Academic Management System (Python / FastAPI / SQLite / Streamlit)
This project demonstrates an incremental, zero-downtime evolution of a small academic domain:
Students, Courses, Enrollments, Teachers, Teachings — applied via in-process migrations.
Files:
 - main.py: FastAPI application (start with uvicorn)
 - api.py: Routers for CRUD endpoints and migration introspection
 - migrations.py: MigrationService that applies the six steps in-process
 - db.py: Database engine and reflection helpers
 - domain/entities.py: Pydantic models / domain vocabulary
 - repositories.py: Data access layer using reflection (adapts to schema changes)
 - services.py: Business logic layer
 - streamlit_app.py: Minimal Streamlit UI for inspection
 - smoke_test.py: Automated smoke test (run after migrations applied)
How to use:
 1. Start the FastAPI server:
    uvicorn main:app --reload
 2. Use the /migrate endpoint to apply steps one-by-one:
    POST http://127.0.0.1:8000/migrate with JSON {"step": 1}
    then {"step": 2}, ... up to {"step": 6}
 3. After applying migration 4 you will be able to CRUD enrollments.
    After applying migration 6 you will be able to CRUD teachings.
 4. Inspect DB with Streamlit:
    streamlit run streamlit_app.py
 5. Run smoke test via:
    POST http://127.0.0.1:8000/smoke
    or run python smoke_test.py
Notes:
 - The repository layer reflects the DB schema for each operation. This avoids restarting
   the server when migrations add tables/columns.
 - Migrations are tracked in a 'migrations' table.