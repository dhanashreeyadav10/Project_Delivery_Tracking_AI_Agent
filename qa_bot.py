import pandas as pd
from llm_groq import explain_insight

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # ---------------- HR / ATTRITION (TABULAR)
    if "leave" in q or "attrition" in q:
        risky = hr_df[hr_df["hr_risk"] == 1]

        if risky.empty:
            return "✅ No immediate attrition risks detected."

        return risky.rename(columns={
            "employee_id":"Employee ID",
            "avg_attendance":"Attendance %",
            "avg_rating":"Performance Rating"
        })

    # ---------------- UTILIZATION
    if "utilization" in q or "bench" in q:
        return util_df[util_df["utilization_pct"] < 60]

    # ---------------- DELIVERY RISK
    if "risk" in q or "delay" in q:
        return risk_df[risk_df["risk_flag"] == 1]

    # ---------------- COST / MARGIN
    if "cost" in q or "margin" in q or "loss" in q:
        return cost_df[cost_df["margin"] < 0]

    # ---------------- EXECUTIVE
    prompt = f"""
    You are a senior delivery leader.

    Question:
    {question}

    Provide:
    - Insight
    - Business impact
    - Recommendations
    """
    return explain_insight(prompt)
