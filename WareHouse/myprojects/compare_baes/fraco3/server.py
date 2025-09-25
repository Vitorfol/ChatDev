from fastapi import FastAPI
from routers import router
from database import engine, Base

def create_app():
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title="School API")
    app.include_router(router, prefix="/api")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
