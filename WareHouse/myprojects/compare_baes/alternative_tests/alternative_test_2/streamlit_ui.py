'''
Minimal Streamlit UI for inspection and simple interactions with the backend API.
This UI focuses on listing entities and performing simple create/enroll/assign operations.
Run with: streamlit run streamlit_ui.py
'''
import streamlit as st
import requests
API_BASE = "http://localhost:8000/api"
st.set_page_config(page_title="Academic Management - Inspect", layout="wide")
st.title("Academic Management - Minimal UI")
col1, col2, col3 = st.columns(3)
# Helper functions
def fetch(path):
    try:
        r = requests.get(API_BASE + path)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Error fetching {path}: {e}")
        return None
def post(path, payload):
    try:
        r = requests.post(API_BASE + path, json=payload)
        r.raise_for_status()
        return r.json() if r.content else {}
    except requests.HTTPError as he:
        try:
            st.error(f"API error: {r.json()}")
        except Exception:
            st.error(f"HTTP error: {he}")
        return None
    except Exception as e:
        st.error(f"Error posting {path}: {e}")
        return None
with col1:
    st.header("Students")
    students = fetch("/students") or []
    for s in students:
        st.write(f"{s['id']}: {s['name']} — {s['email']}")
    st.subheader("Create Student")
    with st.form("create_student"):
        name = st.text_input("Name")
        email = st.text_input("Email")
        submitted = st.form_submit_button("Create")
        if submitted:
            result = post("/students", {"name": name, "email": email})
            if result is not None:
                st.success("Created student")
                st.experimental_rerun()
with col2:
    st.header("Courses")
    courses = fetch("/courses") or []
    for c in courses:
        st.write(f"{c['id']}: {c['title']} — {c['level']}")
    st.subheader("Create Course")
    with st.form("create_course"):
        title = st.text_input("Title")
        level = st.text_input("Level")
        submitted = st.form_submit_button("Create")
        if submitted:
            result = post("/courses", {"title": title, "level": level})
            if result is not None:
                st.success("Created course")
                st.experimental_rerun()
with col3:
    st.header("Teachers")
    teachers = fetch("/teachers") or []
    for t in teachers:
        st.write(f"{t['id']}: {t['name']} — {t['department']}")
    st.subheader("Create Teacher")
    with st.form("create_teacher"):
        name = st.text_input("Name", key="tname")
        dept = st.text_input("Department", key="tdept")
        submitted = st.form_submit_button("Create Teacher")
        if submitted:
            result = post("/teachers", {"name": name, "department": dept})
            if result is not None:
                st.success("Created teacher")
                st.experimental_rerun()
st.markdown("---")
st.subheader("Enrollments")
students = fetch("/students") or []
courses = fetch("/courses") or []
if students and courses:
    with st.form("enroll_form"):
        sid = st.selectbox("Student", options=[(s["id"], s["name"]) for s in students], format_func=lambda x: f"{x[0]} - {x[1]}")
        cid = st.selectbox("Course", options=[(c["id"], c["title"]) for c in courses], format_func=lambda x: f"{x[0]} - {x[1]}")
        submitted = st.form_submit_button("Enroll")
        if submitted:
            payload = {"student_id": sid[0], "course_id": cid[0]}
            result = post("/enrollments", payload)
            if result is not None:
                st.success("Enrolled")
                st.experimental_rerun()
else:
    st.info("Add students and courses to create enrollments.")
enrollments = fetch("/enrollments") or []
if enrollments:
    for e in enrollments:
        st.write(f"Student {e['student_id']} enrolled in Course {e['course_id']}")
st.markdown("---")
st.subheader("Teachings")
teachers = fetch("/teachers") or []
courses = fetch("/courses") or []
if teachers and courses:
    with st.form("assign_form"):
        tid = st.selectbox("Teacher", options=[(t["id"], t["name"]) for t in teachers], format_func=lambda x: f"{x[0]} - {x[1]}")
        cid = st.selectbox("Course for assignment", options=[(c["id"], c["title"]) for c in courses], format_func=lambda x: f"{x[0]} - {x[1]}")
        submitted = st.form_submit_button("Assign")
        if submitted:
            payload = {"teacher_id": tid[0], "course_id": cid[0]}
            result = post("/teachings", payload)
            if result is not None:
                st.success("Assigned")
                st.experimental_rerun()
else:
    st.info("Add teachers and courses to create assignments.")
teachings = fetch("/teachings") or []
if teachings:
    for t in teachings:
        st.write(f"Teacher {t['teacher_id']} assigned to Course {t['course_id']}")
st.markdown("----")
st.write("This UI is minimal and intended for quick inspection of the backend. Use the API for full control.")