'''
Main FastAPI application entrypoint. Sets up database engine, applies migrations at startup,
and includes API routers for students, courses, enrollments, teachers, and course-teacher assignments.
'''
'''
Main FastAPI application entrypoint. Sets up database engine, applies migrations at startup,
and includes API routers for students, courses, enrollments, teachers, and course-teacher assignments.
'''
from fastapi import FastAPI
import os
from db import get_engine, init_db_session
from migrate import apply_migrations
# Routers are local modules (not inside a routers package) to match repository layout.
import students
import courses
import enrollments
import teachers
import course_teachers
DB_PATH = os.path.join(os.path.dirname(__file__), "chatdev.db")
MIGRATIONS_DIR = os.path.join(os.path.dirname(__file__), "migrations")
app = FastAPI(title="ChatDev School API")
# Include routers
app.include_router(students.router, prefix="/students", tags=["students"])
app.include_router(courses.router, prefix="/courses", tags=["courses"])
app.include_router(enrollments.router, prefix="/enrollments", tags=["enrollments"])
app.include_router(teachers.router, prefix="/teachers", tags=["teachers"])
app.include_router(course_teachers.router, prefix="/course-teachers", tags=["course-teachers"])
@app.on_event("startup")
def startup():
    """
    Apply migrations and initialize DB sessionmaker on application startup.
    """
    # Ensure DB file exists by creating engine
    engine = get_engine(DB_PATH)
    # Apply migrations (in-process)
    apply_migrations(DB_PATH, MIGRATIONS_DIR)
    # Initialize sessionmaker
    init_db_session(engine)