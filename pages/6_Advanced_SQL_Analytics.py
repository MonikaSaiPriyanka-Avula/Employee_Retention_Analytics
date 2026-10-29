import streamlit as st
import pandas as pd
import plotly.express as px
from database import db_health, query_df, list_tables, table_columns

st.set_page_config(page_title="Advanced SQL Analytics", page_icon="🧮", layout="wide")
st.title("Advanced SQL Analytics")
if not db_health()["ok"]:
    st.error("MySQL connection failed."); st.stop()

st.markdown("Use the prebuilt queries below to demonstrate SQL aggregation, grouping, date analytics, and joins.")

choice = st.selectbox("Choose an analysis", [
    "Row counts by table",
    "Attrition label distribution",
    "Outcome types",
    "Engagement survey status",
    "Average engagement by month",
    "Workload hours summary",
    "Employee status distribution",
])

if choice == "Row counts by table":
    rows = []
    for table in list_tables():
        try:
            rows.append({"table_name": table, "row_count": int(query_df(f"SELECT COUNT(*) AS n FROM `{table}`").iloc[0]["n"])})
        except Exception:
            rows.append({"table_name": table, "row_count": None})
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    

elif choice == "Attrition label distribution":
    cols = table_columns("attrition_outcomes")
    label = next((c for c in ["voluntary_attrition_label", "attrition_label", "label"] if c in cols), None)
    if label:
        sql = f"SELECT `{label}` AS label, COUNT(*) AS records FROM attrition_outcomes GROUP BY `{label}` ORDER BY label"
        df = query_df(sql); st.dataframe(df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(df, x="label", y="records", title="Outcome records by label"), use_container_width=True)
        st.code(sql, language="sql")
    else: st.warning(f"Could not find a label field. Columns: {cols}")

elif choice == "Outcome types":
    cols = table_columns("attrition_outcomes")
    if "outcome_type" in cols:
        sql = "SELECT outcome_type, COUNT(*) AS records FROM attrition_outcomes GROUP BY outcome_type ORDER BY records DESC"
        df = query_df(sql); st.dataframe(df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.pie(df, names="outcome_type", values="records"), use_container_width=True); st.code(sql, language="sql")
    else: st.warning(f"outcome_type not found. Columns: {cols}")

elif choice == "Engagement survey status":
    cols = table_columns("engagement_surveys")
    status = next((c for c in ["survey_status", "completion_status", "status"] if c in cols), None)
    if status:
        sql = f"SELECT `{status}` AS survey_status, COUNT(*) AS records FROM engagement_surveys GROUP BY `{status}` ORDER BY records DESC"
        df = query_df(sql); st.dataframe(df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(df, x="survey_status", y="records"), use_container_width=True); st.code(sql, language="sql")
    else: st.warning(f"Status field not detected. Columns: {cols}")

elif choice == "Average engagement by month":
    cols = table_columns("engagement_surveys")
    date = next((c for c in ["survey_date", "observation_date", "snapshot_date"] if c in cols), None)
    score = next((c for c in ["engagement_score", "score", "survey_score"] if c in cols), None)
    if date and score:
        sql = f"SELECT DATE_FORMAT(`{date}`, '%Y-%m') AS month, AVG(`{score}`) AS average_score, COUNT(`{score}`) AS answered_surveys FROM engagement_surveys WHERE `{score}` IS NOT NULL GROUP BY month ORDER BY month"
        df = query_df(sql); st.dataframe(df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.line(df, x="month", y="average_score", markers=True), use_container_width=True); st.code(sql, language="sql")
    else: st.warning(f"Required date/score fields not detected. Columns: {cols}")

elif choice == "Workload hours summary":
    cols = table_columns("workload_snapshots")
    hours = next((c for c in ["weekly_hours", "hours_worked", "work_hours", "total_hours"] if c in cols), None)
    if hours:
        sql = f"SELECT MIN(`{hours}`) AS minimum_hours, AVG(`{hours}`) AS average_hours, MAX(`{hours}`) AS maximum_hours FROM workload_snapshots"
        df = query_df(sql); st.dataframe(df, use_container_width=True, hide_index=True); st.code(sql, language="sql")
    else: st.warning(f"Work-hours field not detected. Columns: {cols}")

else:
    cols = table_columns("employees")
    status = next((c for c in ["employment_status", "status"] if c in cols), None)
    if status:
        sql = f"SELECT `{status}` AS employment_status, COUNT(*) AS employees FROM employees GROUP BY `{status}` ORDER BY employees DESC"
        df = query_df(sql); st.dataframe(df, use_container_width=True, hide_index=True)
        st.plotly_chart(px.pie(df, names="employment_status", values="employees"), use_container_width=True); st.code(sql, language="sql")
    else: st.warning(f"Employee status field not detected. Columns: {cols}")
