import streamlit as st
import pandas as pd
import plotly.express as px
from database import db_health, query_df, table_columns, first_existing, safe_sample

st.set_page_config(page_title="Overview Dashboard", page_icon="📈", layout="wide")
st.title("Overview Dashboard")
health = db_health()
if not health["ok"]:
    st.error(health["error"]); st.stop()

counts = health["counts"]
k1, k2, k3, k4 = st.columns(4)
k1.metric("Employees", f"{(counts.get('employees') or 0):,}")
k2.metric("Tenure snapshots", f"{(counts.get('tenure_snapshots') or 0):,}")
k3.metric("Attrition outcomes", f"{(counts.get('attrition_outcomes') or 0):,}")
k4.metric("Interventions", f"{(counts.get('interventions') or 0):,}")

st.subheader("Records by table")
summary = pd.DataFrame([{"Table": t, "Records": n if n is not None else 0} for t, n in counts.items()])
st.plotly_chart(px.bar(summary, x="Table", y="Records", title="Row counts by table"), use_container_width=True)
st.dataframe(summary, use_container_width=True, hide_index=True)

st.subheader("Available date coverage")
for table in ["tenure_snapshots", "engagement_surveys", "workload_snapshots", "attrition_outcomes"]:
    cols = table_columns(table)
    date_col = first_existing(cols, ["observation_date", "snapshot_date", "survey_date", "event_date"])
    if date_col:
        try:
            dates = query_df(f"SELECT MIN(`{date_col}`) AS first_date, MAX(`{date_col}`) AS last_date FROM `{table}`")
            st.write(f"**{table}** — {dates.iloc[0]['first_date']} to {dates.iloc[0]['last_date']}")
        except Exception:
            pass
