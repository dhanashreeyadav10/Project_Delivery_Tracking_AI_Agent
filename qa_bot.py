import pandas as pd
from llm_groq import explain_insight


def answer_question(question, util_df, risk_df, cost_df, hr_df):
    """
    Answers delivery intelligence questions.

    Returns:
    - pandas.DataFrame for list / factual questions
    - str (LLM-generated) for executive / why / recommendation questions
    """

    if not question:
        return "Please ask a valid question."

    q = question.lower().strip()

    # --------------------------------------------------
    # UTILIZATION / BENCH
    # --------------------------------------------------
    if any(k in q for k in ["underutilized", "bench", "utilization below"]):
        df = util_df[util_df["utilization_pct"] < 60].copy()

        if df.empty:
            return "No employees are currently underutilized."

        df = df.sort_values("utilization_pct")
        return df.head(10)

    # --------------------------------------------------
    # DELIVERY RISK / PROJECT HEALTH
    # --------------------------------------------------
    if any(k in q for k in ["delivery risk", "delay", "risky project"]):
        df = risk_df[risk_df["risk_flag"] == 1].copy()

        if df.empty:
            return "No projects are currently flagged as delivery risks."

        return df

    # --------------------------------------------------
    # COST / MARGIN / FINANCIAL
    # --------------------------------------------------
    if any(k in q for k in ["loss", "margin", "financial", "profit"]):
        df = cost_df[cost_df["margin"] < 0].copy()

        if df.empty:
            return "All projects are currently financially healthy."

        return df

    # --------------------------------------------------
    # HR / ATTRITION
    # --------------------------------------------------
    if any(k in q for k in ["hr risk", "attrition", "likely to leave", "leave company"]):
        df = hr_df[hr_df["hr_risk"] == 1].copy()

        if df.empty:
            return "No employees currently show strong HR or attrition risk signals."

        return df

    # --------------------------------------------------
    # EXECUTIVE / WHY / RECOMMENDATION (LLM)
    # --------------------------------------------------
    prompt = f"""
    You are a senior enterprise delivery leader.

    Question:
    {question}

    Provide:
    - A clear and concise answer
    - Business impact
    - Actionable recommendations for leadership

    Keep the response professional and executive-friendly.
    """

    return explain_insight(prompt)
