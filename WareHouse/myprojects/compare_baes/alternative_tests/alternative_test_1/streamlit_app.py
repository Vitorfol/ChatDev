'''
Minimal Streamlit UI to inspect records. The UI is intentionally minimal per requirements.
Run with: streamlit run streamlit_app.py
'''
'''
Minimal Streamlit UI to inspect records. The UI is intentionally minimal per requirements.
Run with: streamlit run streamlit_app.py
'''
import streamlit as st
import sqlite3
import os
import pandas as pd
DB_PATH = os.path.join(os.path.dirname(__file__), "chatdev.db")
def query_table(table: str):
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        return df
    except Exception:
        return None
    finally:
        conn.close()
st.set_page_config(page_title="ChatDev Viewer", page_icon="📚")
st.title("ChatDev - Minimal DB Viewer")
tables = ["student", "course", "teacher", "enrollment", "course_teacher"]
selected = st.selectbox("Table", options=tables)
df = query_table(selected)
if df is None:
    st.write("No data or table missing.")
else:
    st.dataframe(df)