'''
Minimal Streamlit UI for inspecting records.
This is a very small UI focused on backend inspection. It calls the FastAPI
endpoints to list Students, Courses, Enrollments, Teachers, and Teachings.
Run with: streamlit run streamlit_app.py
'''
import streamlit as st
import requests
API_BASE = st.secrets.get("api_base", "http://localhost:8000")
st.title("Academic Management - Minimal Inspector")
st.markdown("This UI fetches data from the FastAPI backend. Make sure the API is running.")
col1, col2 = st.columns(2)
with col1:
    if st.button("Refresh All"):
        st.experimental_rerun()
with col2:
    if st.button("Apply Next Migration"):
        try:
            r = requests.post(f"{API_BASE}/migrations/apply_next", timeout=5)
            st.write("Migration result:", r.json())
        except Exception as e:
            st.error(f"Migration call failed: {e}")
def list_resource(path):
    try:
        r = requests.get(f"{API_BASE}{path}", timeout=5)
        if r.status_code == 200:
            return r.json()
        return []
    except Exception as e:
        return f"Error: {e}"
st.header("Students")
students = list_resource("/students")
st.write(students)
st.header("Courses")
courses = list_resource("/courses")
st.write(courses)
st.header("Teachers")
teachers = list_resource("/teachers")
st.write(teachers)
st.header("Enrollments")
enrollments = list_resource("/enrollments")
st.write(enrollments)
st.header("Teachings")
teachings = list_resource("/teachings")
st.write(teachings)