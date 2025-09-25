'''
Application module that defines the FastAPI "app" instance and wires the API router.
This module fixes the previous circular-import problem by providing a single
authoritative app object that other modules (including tests) can import.
It also ensures the migration version table exists at startup.
'''
from fastapi import FastAPI
from api import router as api_router
from migrations import migration_manager
app = FastAPI(title="Academic Management")
app.include_router(api_router)
# Ensure migrations bookkeeping exists when the ASGI app starts.
@app.on_event("startup")
def _ensure_migrations_table():
    # Safe to call idempotently; migration manager will create the table if missing.
    migration_manager.ensure_version_table()