import streamlit as st
import pandas as pd
from database import db_health, query_df, table_columns, first_existing

st.set_page_config(page_title="Employee Explorer", page_icon="👥", layout="wide")
st.title("Employee Explorer")
if not db_health()["ok"]:
    st.error("MySQL connection failed."); st.stop()

table = "employees"
cols = table_columns(table)
if not cols:
    st.error("employees table not found."); st.stop()

st.write(f"Available employee fields: {', '.join(cols)}")
id_col = first_existing(cols, ["employee_id", "id"])
dept_col = first_existing(cols, ["department", "department_name"])
team_col = first_existing(cols, ["team_id"])
status_col = first_existing(cols, ["employment_status", "status"])
name_col = first_existing(cols, ["employee_name", "full_name", "name"])

filters = st.columns(3)
search = filters[0].text_input("Search employee ID/name")
status_filter = None
if status_col:
    status_values = query_df(f"SELECT DISTINCT `{status_col}` AS v FROM `{table}` WHERE `{status_col}` IS NOT NULL ORDER BY v")
    opts = ["All"] + status_values["v"].astype(str).tolist()
    selected_status = filters[1].selectbox("Employment status", opts)
    if selected_status != "All":
        status_filter = selected_status
team_filter = None
if team_col:
    team_values = query_df(f"SELECT DISTINCT `{team_col}` AS v FROM `{table}` WHERE `{team_col}` IS NOT NULL ORDER BY v")
    team_opts = ["All"] + team_values["v"].astype(str).tolist()
    selected_team = filters[2].selectbox("Team ID", team_opts)
    if selected_team != "All":
        team_filter = selected_team

where = []
params = []
if search and id_col:
    if name_col:
        where.append(f"(CAST(`{id_col}` AS CHAR) LIKE %s OR CAST(`{name_col}` AS CHAR) LIKE %s)")
        params.extend([f"%{search}%", f"%{search}%"])
    else:
        where.append(f"CAST(`{id_col}` AS CHAR) LIKE %s")
        params.append(f"%{search}%")
if status_filter is not None:
    where.append(f"`{status_col}` = %s"); params.append(status_filter)
if team_filter is not None:
    where.append(f"CAST(`{team_col}` AS CHAR) = %s"); params.append(team_filter)

sql = f"SELECT * FROM `{table}`" + (" WHERE " + " AND ".join(where) if where else "") + " LIMIT 1000"
df = query_df(sql, tuple(params))
st.metric("Employees shown (max 1,000)", f"{len(df):,}")
st.dataframe(df, use_container_width=True, hide_index=True)
st.download_button("Download displayed employees as CSV", df.to_csv(index=False).encode("utf-8"), "employees_filtered.csv", "text/csv")
