import streamlit as st
import pandas as pd
from database import db_health, query_df, list_tables, table_columns, EXPECTED_TABLES

st.set_page_config(page_title="Data Quality", page_icon="🧪", layout="wide")
st.title("Data Quality Checks")
health = db_health()
if not health["ok"]:
    st.error(health["error"]); st.stop()

tables = list_tables()
table_report = pd.DataFrame([
    {"Table": t, "Exists": t in tables, "Rows": health["counts"].get(t)}
    for t in EXPECTED_TABLES
])
st.subheader("Expected table availability")
st.dataframe(table_report, use_container_width=True, hide_index=True)

results = []
def add_result(name, status, details):
    results.append({"Check": name, "Status": status, "Details": details})

if "employees" in tables:
    df = query_df("SELECT COUNT(*) AS total, COUNT(DISTINCT employee_id) AS unique_ids FROM employees")
    total, unique_ids = int(df.iloc[0]["total"]), int(df.iloc[0]["unique_ids"])
    add_result("Employee ID uniqueness", "PASS" if total == unique_ids else "FAIL", f"{unique_ids:,} unique IDs / {total:,} rows")
else:
    add_result("Employee ID uniqueness", "SKIP", "employees table missing")

if "attrition_outcomes" in tables:
    cols = table_columns("attrition_outcomes")
    label = next((c for c in ["voluntary_attrition_label", "attrition_label", "label"] if c in cols), None)
    if label:
        df = query_df(f"SELECT COUNT(*) AS total, SUM(CASE WHEN `{label}` NOT IN (0,1) OR `{label}` IS NULL THEN 1 ELSE 0 END) AS invalid FROM attrition_outcomes")
        invalid = int(df.iloc[0]["invalid"] or 0)
        add_result("Attrition label domain", "PASS" if invalid == 0 else "FAIL", f"{invalid:,} invalid labels")
    else:
        add_result("Attrition label domain", "SKIP", f"No recognized label column. Available columns: {cols}")
else:
    add_result("Attrition label domain", "SKIP", "attrition_outcomes table missing")

for table in ["tenure_snapshots", "attrition_outcomes", "workload_snapshots", "engagement_surveys"]:
    if table not in tables or "employees" not in tables:
        add_result(f"{table} employee references", "SKIP", "Required table missing")
        continue
    cols = table_columns(table)
    if "employee_id" not in cols:
        add_result(f"{table} employee references", "SKIP", "employee_id column missing")
        continue
    df = query_df(f"SELECT COUNT(*) AS n FROM `{table}` t LEFT JOIN employees e ON t.employee_id=e.employee_id WHERE e.employee_id IS NULL")
    n = int(df.iloc[0]["n"])
    add_result(f"{table} employee references", "PASS" if n == 0 else "FAIL", f"{n:,} orphan rows")

report = pd.DataFrame(results)
st.subheader("Validation results")
st.dataframe(report, use_container_width=True, hide_index=True)
failed = int((report["Status"] == "FAIL").sum())

