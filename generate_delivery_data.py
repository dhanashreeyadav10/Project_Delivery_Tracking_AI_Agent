import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

NUM_ROWS = 1000

employees = [f"E{str(i).zfill(4)}" for i in range(1, 201)]
projects = [f"P{str(i).zfill(3)}" for i in range(1, 31)]
managers = [f"M{str(i).zfill(2)}" for i in range(1, 16)]

departments = ["Engineering", "QA", "Data", "DevOps"]
designations = ["Associate", "Senior Engineer", "Lead", "Manager"]
employment_types = ["Full-Time", "Contractor"]
locations = ["Bangalore", "Pune", "Chennai", "Hyderabad"]
clients = ["ABC Bank", "XYZ Retail", "FinCorp", "HealthPlus"]
project_types = ["Fixed", "Time & Material"]
task_types = ["Development", "Testing", "Support", "Design"]
priorities = ["Low", "Medium", "High", "Critical"]
ticket_statuses = ["To Do", "In Progress", "Done"]

rows = []

for _ in range(NUM_ROWS):
    emp = random.choice(employees)
    proj = random.choice(projects)

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    work_date = start_date + timedelta(days=random.randint(0, 300))

    rows.append({
        "employee_id": emp,
        "employee_name": f"Employee_{emp}",
        "department": random.choice(departments),
        "designation": random.choice(designations),
        "employment_type": random.choice(employment_types),
        "location": random.choice(locations),
        "experience_years": random.randint(1, 12),
        "cost_per_hour": random.randint(600, 2200),
        "manager_id": random.choice(managers),
        "project_id": proj,
        "project_name": f"Project_{proj}",
        "client_name": random.choice(clients),
        "project_type": random.choice(project_types),
        "start_date": start_date.date(),
        "end_date": end_date.date(),
        "planned_hours": random.randint(800, 2400),
        "billing_rate": random.randint(1800, 4500),
        "work_date": work_date.date(),
        "hours_logged": random.randint(1, 10),
        "billable": random.choice([0, 1]),
        "task_type": random.choice(task_types),
        "jira_ticket": f"JIRA-{random.randint(1000, 9999)}",
        "ticket_status": random.choice(ticket_statuses),
        "priority": random.choice(priorities),
        "story_points": random.randint(1, 13),
        "attendance_pct": random.randint(85, 100),
        "leave_days": random.randint(0, 6),
        "performance_rating": round(random.uniform(3.0, 5.0), 1)
    })

df = pd.DataFrame(rows)
df.to_csv("delivery_intelligence_1000.csv", index=False)

print("✅ delivery_intelligence_1000.csv generated successfully")
