'''
Minimal Streamlit UI for inspecting records in the SQLite database.
This app reads the current tables (if they exist) and displays their rows.
Run with: streamlit run streamlit_app.py
'''
import streamlit as st
import sqlite3
from db import connect_db
st.title("Academic Management - Live DB Inspector")
def read_table(conn: sqlite3.Connection, table_name: str):
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
    if cur.fetchone() is None:
        return None
    cur = conn.execute(f"SELECT * FROM {table_name};")
    rows = cur.fetchall()
    return rows
conn = connect_db()
st.write("Database file:", st.text_input("DB Path", value="academic.db", disabled=True))
for table in ["student", "course", "teacher", "enrollment", "teaching", "migrations"]:
    rows = read_table(conn, table)
    if rows is None:
        st.info(f"Table '{table}' does not exist yet.")
    else:
        st.subheader(f"Table: {table} (rows: {len(rows)})")
        if len(rows) > 0:
            # Convert sqlite3.Row to dicts to show nicely
            colnames = rows[0].keys()
            data = [tuple(r) for r in rows]
            st.write(colnames)
            st.write(data)
conn.close()