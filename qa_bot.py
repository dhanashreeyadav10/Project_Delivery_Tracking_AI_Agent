import pandas as pd
from llm_groq import explain_insight

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # ---------------- UTILIZATION ----------------
    if any(k in q for k in ["underutilized", "bench", "utilization below"]):
        df = util_df[util_df["utilization_pct"] < 60].sort_values("utilization_pct")
        return df.head(10)

    # ---------------- DELIVERY RISK ----------------
    if any(k in q for k in ["delivery risk", "delay", "risky projects"]):
        df = risk_df[risk_df["risk_flag"] == 1]
        return df

    # ---------------- FINANCIAL ----------------
    if any(k in q for k in ["loss", "margin", "financial"]):
        df = cost_df[cost_df["margin"] < 0]
        return df

    # ---------------- HR / ATTRITION ----------------
    if any(k in q for k in ["hr risk", "attrition", "likely to leave"]):
        df = hr_df[hr_df["hr_risk"] == 1]
        return df

    # ---------------- EXECUTIVE / WHY ----------------
    prompt = f"""
    You are a senior delivery leader.

    Question:
    {question}

    Provide:
    - Clear answer
    - Business impact
    - Actionable recommendation
    """

    return explain_insight(prompt)
