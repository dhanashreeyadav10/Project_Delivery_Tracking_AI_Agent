from llm_groq import explain_insight
import pandas as pd

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # -----------------------------
    # ATTRITION / HR RISK (TABULAR)
    # -----------------------------
    if "leave" in q or "attrition" in q:
        risky = hr_df[hr_df["hr_risk"] == 1]

        if risky.empty:
            return "✅ No immediate attrition risks detected based on attendance and performance trends."

        # Ensure safe merge
        output = risky.copy()
        output["employee_id"] = output["employee_id"].astype(str)

        return output[[
            "employee_id",
            "avg_attendance",
            "avg_rating"
        ]].rename(columns={
            "avg_attendance": "Attendance %",
            "avg_rating": "Performance Rating"
        })

    # -----------------------------
    # UTILIZATION / BENCH
    # -----------------------------
    if "utilization" in q or "bench" in q:
        data = util_df[util_df["utilization_pct"] < 60]
        summary = f"{len(data)} employees are underutilized."

    # -----------------------------
    # DELIVERY RISK
    # -----------------------------
    elif "risk" in q or "delay" in q:
        data = risk_df[risk_df["risk_flag"] == 1]
        summary = f"{len(data)} projects are at delivery risk."

    # -----------------------------
    # COST / MARGIN
    # -----------------------------
    elif "cost" in q or "margin" in q or "loss" in q:
        data = cost_df[cost_df["margin"] < 0]
        summary = f"{len(data)} projects are loss-making."

    else:
        summary = "Overall delivery, HR, and financial health overview."
        data = None

    prompt = f"""
    You are a senior enterprise delivery leader.

    Question:
    {question}

    Insight:
    {summary}

    Provide:
    - Why this matters
    - Business impact
    - Clear recommendations
    """

    return explain_insight(prompt)
