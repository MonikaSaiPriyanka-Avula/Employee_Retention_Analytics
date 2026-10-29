import streamlit as st
import pandas as pd
import plotly.express as px
from database import db_health, query_df, table_columns, first_existing

st.set_page_config(page_title="Engagement Analysis", page_icon="💬", layout="wide")
st.title("Engagement Analysis")
if not db_health()["ok"]:
    st.error("MySQL connection failed."); st.stop()

table = "engagement_surveys"
cols = table_columns(table)
if not cols:
    st.error("engagement_surveys table not found."); st.stop()

status_col = first_existing(cols, ["survey_status", "completion_status", "status"])
score_col = first_existing(cols, ["engagement_score", "score", "survey_score"])
date_col = first_existing(cols, ["survey_date", "observation_date", "snapshot_date"])
emp_col = first_existing(cols, ["employee_id"])

a, b, c = st.columns(3)
a.metric("Survey records", f"{int(query_df('SELECT COUNT(*) n FROM engagement_surveys').iloc[0]['n']):,}")
if status_col:
    status = query_df(f"SELECT `{status_col}` AS status, COUNT(*) AS records FROM `{table}` GROUP BY `{status_col}` ORDER BY records DESC")
    completed = int(status.loc[status["status"].astype(str).str.upper().eq("COMPLETED"), "records"].sum())
    total = int(status["records"].sum())
    b.metric("Completed surveys", f"{completed:,}")
    c.metric("Completion rate", f"{completed/total:.1%}" if total else "N/A")
    st.subheader("Survey submission status")
    st.plotly_chart(px.pie(status, names="status", values="records", title="Survey records by status"), use_container_width=True)
    st.dataframe(status, use_container_width=True, hide_index=True)

if score_col:
    score_df = query_df(f"SELECT `{score_col}` AS score, COUNT(*) AS records FROM `{table}` WHERE `{score_col}` IS NOT NULL GROUP BY `{score_col}` ORDER BY `{score_col}`")
    st.subheader("Engagement score distribution")
    st.plotly_chart(px.bar(score_df, x="score", y="records", title="Survey scores (non-missing only)"), use_container_width=True)
    avg = query_df(f"SELECT AVG(`{score_col}`) AS avg_score FROM `{table}` WHERE `{score_col}` IS NOT NULL")
    st.metric("Average recorded score", f"{float(avg.iloc[0]['avg_score']):.2f}" if pd.notna(avg.iloc[0]["avg_score"]) else "N/A")
    st.caption("Missing or not-submitted surveys are not treated as low engagement.")

if date_col and score_col:
    trend = query_df(f"SELECT DATE_FORMAT(`{date_col}`, '%Y-%m') AS month, AVG(`{score_col}`) AS average_score FROM `{table}` WHERE `{score_col}` IS NOT NULL GROUP BY month ORDER BY month")
    st.subheader("Monthly average engagement")
    st.plotly_chart(px.line(trend, x="month", y="average_score", markers=True, title="Monthly average of recorded survey scores"), use_container_width=True)

preview = [c for c in [emp_col, date_col, status_col, score_col] if c]
if preview:
    st.subheader("Survey data preview")
    st.dataframe(query_df("SELECT " + ", ".join(f"`{c}`" for c in preview) + f" FROM `{table}` LIMIT 500"), use_container_width=True, hide_index=True)
