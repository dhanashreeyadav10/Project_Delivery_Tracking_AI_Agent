import pandas as pd
from llm_groq import explain_insight

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # ------------------------------
    # UTILIZATION
    # ------------------------------
    if "utilization" in q or "under" in q or "bench" in q:
        data = util_df[util_df["utilization_pct"] < 60]

        if data.empty:
            return "No underutilized employees found."

        table = data.sort_values("utilization_pct").head(10)

        response = "Underutilized Employees (Top 10):\n\n"
        for _, r in table.iterrows():
            response += f"- {r['employee_id']} | {r['utilization_pct']:.1f}% utilization\n"

        return response

    # ------------------------------
    # DELIVERY RISK
    # ------------------------------
    if "risk" in q or "delay" in q:
        data = risk_df[risk_df["risk_flag"] == 1]

        if data.empty:
            return "No delivery risk projects found."

        response = "High Delivery Risk Projects:\n\n"
        for _, r in data.iterrows():
            response += f"- Project {r['project_id']} | Open Tickets: {r['open_tickets']}\n"

        return response

    # ------------------------------
    # COST / MARGIN
    # ------------------------------
    if "cost" in q or "margin" in q or "loss" in q:
        data = cost_df[cost_df["margin"] < 0]

        if data.empty:
            return "No loss-making projects found."

        response = "Loss-Making Projects:\n\n"
        for _, r in data.iterrows():
            response += f"- Project {r['project_id']} | Margin: {int(r['margin'])}\n"

        return response

    # ------------------------------
    # HR
    # ------------------------------
    if "hr" in q or "attendance" in q or "attrition" in q:
        data = hr_df[hr_df["hr_risk"] == 1]

        if data.empty:
            return "No HR risk employees found."

        response = "HR Risk Employees:\n\n"
        for _, r in data.iterrows():
            response += f"- {r['employee_id']} | Attendance: {r['avg_attendance']:.1f}%\n"

        return response

    # ------------------------------
    # FALLBACK (LLM OPTIONAL)
    # ------------------------------
    explanation = explain_insight(question)

    if explanation:
        return explanation

    return "Please ask about utilization, delivery risk, HR, or margin."
