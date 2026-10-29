import streamlit as st
import pandas as pd
import plotly.express as px
from database import db_health, query_df, table_columns, first_existing

st.set_page_config(page_title="Workload Analysis", page_icon="⏱️", layout="wide")
st.title("Workload Analysis")
if not db_health()["ok"]:
    st.error("MySQL connection failed."); st.stop()

table = "workload_snapshots"
cols = table_columns(table)
if not cols:
    st.error("workload_snapshots table not found."); st.stop()

date_col = first_existing(cols, ["observation_date", "snapshot_date"])
emp_col = first_existing(cols, ["employee_id"])
hours_col = first_existing(cols, ["weekly_hours", "hours_worked", "work_hours", "total_hours"])
overtime_col = first_existing(cols, ["overtime_hours", "weekly_overtime_hours"])
level_col = first_existing(cols, ["workload_level", "workload_status", "workload_category"])

count = int(query_df(f"SELECT COUNT(*) n FROM `{table}`").iloc[0]["n"])
st.metric("Workload snapshot records", f"{count:,}")

if hours_col:
    summary = query_df(f"SELECT MIN(`{hours_col}`) AS min_hours, AVG(`{hours_col}`) AS avg_hours, MAX(`{hours_col}`) AS max_hours FROM `{table}`")
    x, y, z = st.columns(3)
    x.metric("Minimum hours", f"{summary.iloc[0]['min_hours']:.1f}" if pd.notna(summary.iloc[0]["min_hours"]) else "N/A")
    y.metric("Average hours", f"{summary.iloc[0]['avg_hours']:.1f}" if pd.notna(summary.iloc[0]["avg_hours"]) else "N/A")
    z.metric("Maximum hours", f"{summary.iloc[0]['max_hours']:.1f}" if pd.notna(summary.iloc[0]["max_hours"]) else "N/A")
    dist = query_df(f"SELECT `{hours_col}` AS hours, COUNT(*) AS records FROM `{table}` WHERE `{hours_col}` IS NOT NULL GROUP BY `{hours_col}` ORDER BY `{hours_col}`")
    st.plotly_chart(px.histogram(dist, x="hours", y="records", title="Distribution of recorded work hours"), use_container_width=True)

if overtime_col:
    overtime = query_df(f"SELECT AVG(`{overtime_col}`) AS avg_overtime, SUM(CASE WHEN `{overtime_col}` > 0 THEN 1 ELSE 0 END) AS overtime_records, COUNT(*) AS total FROM `{table}`")
    x, y = st.columns(2)
    x.metric("Average overtime hours", f"{overtime.iloc[0]['avg_overtime']:.2f}" if pd.notna(overtime.iloc[0]["avg_overtime"]) else "N/A")
    y.metric("Records with overtime", f"{int(overtime.iloc[0]['overtime_records']):,}")

if level_col:
    levels = query_df(f"SELECT `{level_col}` AS workload_level, COUNT(*) AS records FROM `{table}` GROUP BY `{level_col}` ORDER BY records DESC")
    st.plotly_chart(px.bar(levels, x="workload_level", y="records", title="Records by workload category"), use_container_width=True)

if date_col and hours_col:
    trend = query_df(f"SELECT DATE_FORMAT(`{date_col}`, '%Y-%m') AS month, AVG(`{hours_col}`) AS avg_hours FROM `{table}` GROUP BY month ORDER BY month")
    st.subheader("Monthly workload trend")
    st.plotly_chart(px.line(trend, x="month", y="avg_hours", markers=True, title="Average work hours by month"), use_container_width=True)


