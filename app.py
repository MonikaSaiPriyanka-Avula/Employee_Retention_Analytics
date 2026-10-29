import streamlit as st
import pandas as pd
from database import db_health, query_df, list_tables, table_columns, first_existing

st.set_page_config(page_title="Employee Retention Analytics", page_icon="📊", layout="wide")
st.title("📊 Employee Retention Analytics")
st.caption("MySQL-powered, multi-page analytics for workforce trends, engagement, workload, and attrition outcomes.")

health = db_health()
if not health["ok"]:
    st.error("Could not connect to MySQL. Check that MySQL Server is running and your .env settings are correct.")
    st.code(health["error"])
    st.info("Copy .env.example to .env, then set DB_HOST, DB_USER, DB_PASSWORD, and DB_NAME.")
    st.stop()

tables = health["tables"]
counts = health["counts"]
if "employees" not in tables:
    st.error(f"Connected to `{health['database']}`, but the employees table was not found.")
    st.write("Tables found:", tables)
    st.stop()

def count(table):
    return counts.get(table) if counts.get(table) is not None else 0

a, b, c, d = st.columns(4)
a.metric("Employees", f"{count('employees'):,}")
b.metric("Tenure snapshots", f"{count('tenure_snapshots'):,}")
c.metric("Attrition outcome records", f"{count('attrition_outcomes'):,}")
d.metric("Engagement surveys", f"{count('engagement_surveys'):,}")

st.subheader("Database health")
health_df = pd.DataFrame([{"Table": t, "Rows": n if n is not None else "Missing"} for t, n in counts.items()])
st.dataframe(health_df, use_container_width=True, hide_index=True)

st.subheader("Explore the project")
st.markdown("""
Use the pages in the left sidebar:

- **Overview Dashboard** — key database metrics and available data.
- **Attrition Analysis** — voluntary attrition labels and outcome types.
- **Engagement Analysis** — survey completion and score trends.
- **Workload Analysis** — hours, overtime, and workload patterns.
- **Employee Explorer** — searchable employee records.
- **Advanced SQL Analytics** — reusable SQL queries and grouped analysis.
- **Data Quality** — missing tables, invalid labels, and reference checks.
""")

