import pandas as pd
import random
from datetime import datetime, timedelta

employees = [f"E{str(i).zfill(3)}" for i in range(1, 101)]
projects = [f"P{str(i).zfill(2)}" for i in range(1, 11)]

rows = []

for _ in range(500):
    emp = random.choice(employees)
    proj = random.choice(projects)

    rows.append({
        "employee_id": emp,
        "employee_name": f"Emp_{emp}",
        "department": random.choice(["Engineering", "QA", "Data"]),
        "designation": random.choice(["Developer", "Senior Dev", "Lead"]),
        "employment_type": random.choice(["Full-Time", "Contractor"]),
        "location": random.choice(["Bangalore", "Pune", "Chennai"]),
        "experience_years": random.randint(1, 10),
        "cost_per_hour": random.randint(600, 2000),
        "manager_id": f"M{random.randint(1,5)}",
        "project_id": proj,
        "project_name": f"Project_{proj}",
        "client_name": random.choice(["ABC Bank", "XYZ Corp", "RetailCo"]),
        "project_type": random.choice(["Fixed", "T&M"]),
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "planned_hours": random.randint(800, 2000),
        "billing_rate": random.randint(2000, 4000),
        "work_date": (datetime.today() - timedelta(days=random.randint(1,90))).date(),
        "hours_logged": random.randint(1,10),
        "billable": random.choice([0,1]),
        "task_type": random.choice(["Development", "Testing", "Support"]),
        "jira_ticket": f"JIRA-{random.randint(100,999)}",
        "ticket_status": random.choice(["To Do", "In Progress", "Done"]),
        "priority": random.choice(["Low", "Medium", "High", "Critical"]),
        "story_points": random.randint(1,8),
        "attendance_pct": random.randint(85,100),
        "leave_days": random.randint(0,5),
        "performance_rating": round(random.uniform(3.0,5.0),1)
    })

df = pd.DataFrame(rows)
df.to_csv("delivery_intelligence_500.csv", index=False)
