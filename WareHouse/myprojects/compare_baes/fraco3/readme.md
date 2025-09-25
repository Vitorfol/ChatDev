'''
Quick instructions for running the FastAPI server and the GUI client.
'''
1. Install dependencies:
   pip install fastapi uvicorn sqlalchemy pydantic requests
2. Start the API server:
   python main.py
   This will start FastAPI at http://127.0.0.1:8000
3. In a separate terminal, run the GUI client:
   python gui_client.py
API endpoints are available under /api, for example:
- POST /api/students/
- GET  /api/students/
- POST /api/courses/
- POST /api/teachers/
- POST /api/students/{student_id}/enroll/{course_id}
...