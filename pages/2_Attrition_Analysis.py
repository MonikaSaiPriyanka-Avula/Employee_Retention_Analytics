import streamlit as st
import pandas as pd
import plotly.express as px
from database import db_health, query_df, table_columns, first_existing

st.set_page_config(page_title="Attrition Analysis", page_icon="🧭", layout="wide")
st.title("Attrition Analysis")
if not db_health()["ok"]:
    st.error("MySQL connection failed."); st.stop()

table = "attrition_outcomes"
cols = table_columns(table)
if not cols:
    st.error("Table attrition_outcomes was not found."); st.stop()

label_col = first_existing(cols, ["voluntary_attrition_label", "attrition_label", "label"])
type_col = first_existing(cols, ["outcome_type", "exit_type"])
date_col = first_existing(cols, ["observation_date", "snapshot_date"])
emp_col = first_existing(cols, ["employee_id"])

if label_col:
    df = query_df(f"SELECT `{label_col}` AS label, COUNT(*) AS records FROM `{table}` GROUP BY `{label_col}` ORDER BY `{label_col}`")
    total = int(df["records"].sum()) if not df.empty else 0
    positives = int(df.loc[df["label"] == 1, "records"].sum()) if not df.empty else 0
    a, b, c = st.columns(3)
    a.metric("Outcome records", f"{total:,}")
    b.metric("Positive voluntary attrition labels", f"{positives:,}")
    c.metric("Positive label share", f"{positives / total:.1%}" if total else "N/A")
    st.caption("Positive label share is the share of observation records labeled positive, not the company's employee-level annual attrition rate.")
    st.plotly_chart(px.bar(df, x="label", y="records", title="Outcome records by voluntary attrition label"), use_container_width=True)
else:
    st.warning("Could not detect a label column. Available columns:")
    st.write(cols)

if type_col:
    by_type = query_df(f"SELECT `{type_col}` AS outcome_type, COUNT(*) AS records FROM `{table}` GROUP BY `{type_col}` ORDER BY records DESC")
    st.subheader("Outcome types")
    st.plotly_chart(px.pie(by_type, names="outcome_type", values="records", title="Records by outcome type"), use_container_width=True)
    st.dataframe(by_type, use_container_width=True, hide_index=True)

if date_col and label_col:
    trend = query_df(f"SELECT DATE_FORMAT(`{date_col}`, '%Y-%m') AS month, `{label_col}` AS label, COUNT(*) AS records FROM `{table}` GROUP BY month, label ORDER BY month")
    st.subheader("Monthly outcome records")
    st.plotly_chart(px.line(trend, x="month", y="records", color="label", markers=True, title="Monthly records by label"), use_container_width=True)

st.subheader("Inspect outcome records")
preview_cols = [c for c in [emp_col, date_col, label_col, type_col, "horizon_months", "outcome_date"] if c and c in cols]
if preview_cols:
    st.dataframe(query_df("SELECT " + ", ".join(f"`{c}`" for c in preview_cols) + f" FROM `{table}` LIMIT 500"), use_container_width=True, hide_index=True)
