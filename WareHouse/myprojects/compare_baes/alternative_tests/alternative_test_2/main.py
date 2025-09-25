'''
Main FastAPI application entrypoint. Sets up the app, includes routers, and runs migrations on startup.
'''
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import router as api_router
from migrations import run_migrations
app = FastAPI(title="Academic Management System")
# Allow Streamlit local UI or any local dev origin to access the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api")
@app.on_event("startup")
def startup_event():
    """
    Run DB migrations on startup. This is a simple zero-downtime migration runner
    that applies any new SQL migration files found in the migrations/ directory.
    """
    run_migrations()