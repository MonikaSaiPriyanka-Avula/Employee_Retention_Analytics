# Employee Retention Analytics

A multi-page Streamlit application using MySQL for employee lifecycle, attrition outcome, engagement survey, and workload analytics.

## Pages
1. Overview Dashboard
2. Attrition Analysis
3. Engagement Analysis
4. Workload Analysis
5. Employee Explorer
6. Advanced SQL Analytics
7. Data Quality Checks

The app reads your existing `employee_retention_analytics` MySQL database. It does not insert, delete, or modify employee data.

## 1. Requirements
- Python 3.10+
- MySQL Server running
- Existing database `employee_retention_analytics` and its tables

## 2. Setup (Windows / VS Code)
Open a terminal in this project folder:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and update your MySQL details:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=employee_retention_analytics
```

Keep `.env` private. Do not upload it to GitHub or share your password.

## 3. Run
```powershell
streamlit run app.py
```

Streamlit opens a local browser tab. Use the left sidebar to switch pages.

## 4. Troubleshooting
- **Access denied**: check `DB_USER` and `DB_PASSWORD` in `.env`.
- **Can't connect / connection refused**: start MySQL Server and check port 3306.
- **Unknown database**: check `DB_NAME` spelling in `.env`.
- **Table not found**: check that the schema was created in the selected database.
- **Column not detected**: open the relevant page; it shows the available columns or a warning. Add the actual column name to that page's candidate list if your schema uses a different name.

## Data interpretation notes
- `voluntary_attrition_label` is the known label field in `attrition_outcomes`.
- A positive label share across snapshot/outcome rows is not automatically the company annual attrition rate.
- `outcome_type` distinguishes VOLUNTARY, INVOLUNTARY, INTERNAL_TRANSFER, OTHER, and NONE.
- Missing survey scores are not treated as low engagement.
- Use analytics to support human-reviewed retention conversations, not automatic employment decisions.
- If the source data is synthetic/demo data, label it clearly in any report or presentation.
