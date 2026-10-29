USE employee_retention_analytics;

-- Table counts
SELECT 'employees' AS table_name, COUNT(*) AS total_rows FROM employees
UNION ALL SELECT 'roles', COUNT(*) FROM roles
UNION ALL SELECT 'teams', COUNT(*) FROM teams
UNION ALL SELECT 'tenure_snapshots', COUNT(*) FROM tenure_snapshots
UNION ALL SELECT 'engagement_surveys', COUNT(*) FROM engagement_surveys
UNION ALL SELECT 'workload_snapshots', COUNT(*) FROM workload_snapshots
UNION ALL SELECT 'attrition_outcomes', COUNT(*) FROM attrition_outcomes;

-- Employee ID uniqueness
SELECT COUNT(*) AS total_rows, COUNT(DISTINCT employee_id) AS unique_employee_ids
FROM employees;

-- Voluntary attrition label domain
SELECT voluntary_attrition_label, outcome_type, COUNT(*) AS records
FROM attrition_outcomes
GROUP BY voluntary_attrition_label, outcome_type
ORDER BY voluntary_attrition_label, outcome_type;

-- Orphan references
SELECT COUNT(*) AS orphan_snapshots
FROM tenure_snapshots t
LEFT JOIN employees e ON t.employee_id = e.employee_id
WHERE e.employee_id IS NULL;

SELECT COUNT(*) AS orphan_outcomes
FROM attrition_outcomes a
LEFT JOIN employees e ON a.employee_id = e.employee_id
WHERE e.employee_id IS NULL;
