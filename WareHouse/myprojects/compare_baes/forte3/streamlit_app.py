'''
Minimal Streamlit UI for inspecting records in the academic.db database.
Run with:
    streamlit run streamlit_app.py
The UI reflects the running database and shows existing tables and their rows.
It is intentionally simple: focus is on backend functionality and schema evolution.
'''
import streamlit as st
import pandas as pd
from db import engine
from sqlalchemy import text, inspect
from db import table_exists, reflect_table
from db import get_table_columns
st.set_page_config(page_title="Academic Management Inspector", layout="wide")
st.title("Academic Management - Inspector")
inspector = None
try:
    from sqlalchemy import inspect as sa_inspect
    inspector = sa_inspect(engine)
except Exception:
    inspector = None
def list_tables():
    if inspector:
        return inspector.get_table_names()
    else:
        # fallback: query sqlite_master
        with engine.connect() as conn:
            res = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            return [row[0] for row in res if row[0] != "sqlite_sequence"]
tables = list_tables()
st.sidebar.header("Database Tables")
selected = st.sidebar.selectbox("Table", options=["-- none --"] + tables)
st.write("Known tables:", tables)
if selected and selected != "-- none --":
    st.subheader(f"Table: {selected}")
    cols = get_table_columns(selected)
    colnames = [c["name"] for c in cols]
    st.write("Columns:", colnames)
    try:
        tbl = reflect_table(selected)
        with engine.connect() as conn:
            res = conn.execute(text(f"SELECT * FROM {selected}"))
            rows = [dict(r._mapping) for r in res]
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df)
        else:
            st.write("No rows found")
    except Exception as e:
        st.error(str(e))
st.sidebar.markdown("---")
st.sidebar.write("Tip: Use the main FastAPI /migrate endpoint to evolve the schema from step 1 to 6.")
st.sidebar.write("API docs available at http://127.0.0.1:8000/docs (when main app running).")