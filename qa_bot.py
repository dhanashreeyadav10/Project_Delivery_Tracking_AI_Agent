import pandas as pd
from llm_groq import explain_insight

def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # ------------------------------------------------
    # TEAM / DEPARTMENT UTILIZATION
    # ------------------------------------------------
    if "team" in q or "department" in q:
        team_util = (
            data.groupby("department")["hours_logged"]
            .sum()
            .reset_index()
        )
        team_util["utilization_pct"] = (team_util["hours_logged"] / 160) * 100

        low_teams = team_util.sort_values("utilization_pct").head(5)

        response = "Teams with Low Utilization:\n\n"
        for _, r in low_teams.iterrows():
            response += f"- {r['department']} | {r['utilization_pct']:.1f}% utilization\n"

        return response

    # ------------------------------------------------
    # EMPLOYEE UTILIZATION
    # ------------------------------------------------
    if "utilization" in q or "bench" in q or "under" in q:
        data_u = util_df[util_df["utilization_pct"] < 60]

        response = "Underutilized Employees (Top 10):\n\n"
        for _, r in data_u.sort_values("utilization_pct").head(10).iterrows():
            response += f"- {r['employee_id']} | {r['utilization_pct']:.1f}% utilization\n"

        return response

    # ------------------------------------------------
    # DELIVERY RISK
    # ------------------------------------------------
    if "risk" in q or "delay" in q:
        risky = risk_df[risk_df["risk_flag"] == 1]

        response = "Delivery Risk Projects:\n\n"
        for _, r in risky.iterrows():
            response += f"- Project {r['project_id']} | Open Tickets: {r['open_tickets']}\n"

        return response

    # ------------------------------------------------
    # COST / MARGIN
    # ------------------------------------------------
    if "cost" in q or "margin" in q or "loss" in q:
        loss = cost_df[cost_df["margin"] < 0]

        response = "Loss-Making Projects:\n\n"
        for _, r in loss.iterrows():
            response += f"- Project {r['project_id']} | Margin: {int(r['margin'])}\n"

        return response

    # ------------------------------------------------
    # HR RISK
    # ------------------------------------------------
    if "hr" in q or "attendance" in q or "attrition" in q:
        hr_risk = hr_df[hr_df["hr_risk"] == 1]

        response = "HR Risk Employees:\n\n"
        for _, r in hr_risk.iterrows():
            response += f"- {r['employee_id']} | Attendance: {r['avg_attendance']:.1f}%\n"

        return response

    # ------------------------------------------------
    # FALLBACK (OPTIONAL LLM)
    # ------------------------------------------------
    llm_answer = explain_insight(question)
    return llm_answer or "Please ask about teams, utilization, delivery risk, HR, or margin."
