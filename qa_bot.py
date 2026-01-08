import pandas as pd
from llm_groq import explain_insight

STANDARD_MONTHLY_CAPACITY = 160


def is_tabular_request(q: str) -> bool:
    keywords = [
        "list", "name", "employee id", "employee_id",
        "team", "table", "show who", "who are"
    ]
    return any(k in q for k in keywords)


def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower().strip()

    # =========================================================
    # 🔴 ATTRITION / LIKELY TO LEAVE (TOP PRIORITY)
    # =========================================================
    if any(k in q for k in [
        "likely to leave", "attrition",
        "resign", "quit", "leave the company"
    ]):
        risky = hr_df[hr_df["hr_risk"] == 1]

        if risky.empty:
            return "No employees currently show strong attrition risk signals."

        # Build safe employee lookup
        emp_lookup = (
            data[["employee_id", "employee_name", "department"]]
            .drop_duplicates()
            .set_index("employee_id")
        )

        rows = []
        for _, r in risky.iterrows():
            emp_id = r["employee_id"]
            if emp_id not in emp_lookup.index:
                continue

            emp = emp_lookup.loc[emp_id]
            rows.append({
                "Employee ID": emp_id,
                "Employee Name": emp["employee_name"],
                "Team": emp["department"],
                "Avg Attendance (%)": round(r["avg_attendance"], 1),
                "Performance Rating": round(r["avg_rating"], 1)
            })

        df = pd.DataFrame(rows).head(10)

        # -------------------------------
        # ✅ TABULAR OUTPUT (EXPLICIT LIST REQUEST)
        # -------------------------------
        if is_tabular_request(q):
            return df

        # -------------------------------
        # 🧠 EXECUTIVE NARRATIVE (LLM)
        # -------------------------------
        prompt = f"""
You are a Delivery Head reviewing people attrition risk.

Based on the following employee data:
{df.to_dict(orient="records")}

Provide:
- High-level summary
- Key reasons why these employees may leave
- Leadership recommendations

Do NOT repeat the table.
Keep it professional and executive-ready.
"""
        return explain_insight(prompt)

    # =========================================================
    # 🔵 TEAM UTILIZATION
    # =========================================================
    if "team" in q and "utilization" in q:
        team_util = (
            data.groupby("department")
            .agg(
                total_hours=("hours_logged", "sum"),
                employee_count=("employee_id", "nunique")
            )
            .reset_index()
        )

        team_util["Utilization %"] = (
            team_util["total_hours"] /
            (team_util["employee_count"] * STANDARD_MONTHLY_CAPACITY)
        ) * 100

        team_util["Utilization %"] = team_util["Utilization %"].clip(upper=100)
        low_teams = team_util.sort_values("Utilization %").head(5)

        if is_tabular_request(q):
            return low_teams[["department", "Utilization %"]]

        prompt = f"""
You are a Delivery Head.

Low utilization teams:
{low_teams.to_dict(orient="records")}

Explain:
- Why utilization is low
- Business impact
- What actions leadership should take
"""
        return explain_insight(prompt)

    # =========================================================
    # 🔵 DELIVERY RISK
    # =========================================================
    if any(k in q for k in ["delivery risk", "delivery", "delay", "miss deadlines"]):
        risky = risk_df[risk_df["risk_flag"] == 1].head(5)

        if risky.empty:
            return "No projects currently show strong delivery risk."

        if is_tabular_request(q):
            return risky[["project_id", "open_tickets", "high_priority"]]

        prompt = f"""
You are a Program Director.

Risky projects:
{risky.to_dict(orient="records")}

Explain risks and immediate corrective actions.
"""
        return explain_insight(prompt)

    # =========================================================
    # 🔵 FINANCIAL / MARGIN
    # =========================================================
    if any(k in q for k in ["margin", "loss", "financial", "profit", "cost"]):
        loss = cost_df[cost_df["margin"] < 0].head(5)

        if loss.empty:
            return "All projects are financially healthy."

        if is_tabular_request(q):
            return loss[["project_id", "margin", "cost_overrun"]]

        prompt = f"""
You are a Finance & Delivery leader.

Loss-making projects:
{loss.to_dict(orient="records")}

Explain causes and corrective actions.
"""
        return explain_insight(prompt)

    # =========================================================
    # 🔵 FALLBACK
    # =========================================================
    return explain_insight(
        "Answer the following delivery intelligence question professionally:\n"
        + question
    )
