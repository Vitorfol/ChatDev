'''
Quick start guide for the Academic Management System.
'''
# Academic Management System (FastAPI + Streamlit)
Prerequisites:
- Python 3.11
- pip
Install:
pip install -r requirements.txt
Run the API server:
uvicorn main:app --reload
By default the API runs at http://127.0.0.1:8000/api
Open docs at http://127.0.0.1:8000/docs
The first startup will run migrations and create the SQLite DB `academic.db` in the project folder.
Run the Streamlit UI (in another terminal):
streamlit run streamlit_ui.py
This minimal UI uses the API to display and create Students, Courses, Teachers, Enrollments, and Teachings.
Notes:
- The project uses a simple migration runner located in migrations.py which applies SQL files in the migrations/ directory and keeps track of applied migrations in a migrations table.
- Domain-driven structure: models, repositories, services, and API routers are separated.
'''