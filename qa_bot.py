

from llm_groq import explain_insight

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    if "utilization" in q or "bench" in q:
        data = util_df[util_df["utilization_pct"] < 60]
        summary = f"{len(data)} employees are underutilized."

    elif "risk" in q or "delay" in q:
        data = risk_df[risk_df["risk_flag"] == 1]
        summary = f"{len(data)} projects are at delivery risk."

    elif "cost" in q or "margin" in q or "loss" in q:
        data = cost_df[cost_df["margin"] < 0]
        summary = f"{len(data)} projects are loss-making."

    elif "hr" in q or "attrition" in q or "attendance" in q:
        data = hr_df[hr_df["hr_risk"] == 1]
        summary = f"{len(data)} employees show HR risk indicators."

    else:
        summary = "Overall delivery, HR, and financial health overview."
        data = None

    prompt = f"""
    You are an enterprise delivery intelligence advisor.

    User Question:
    {question}

    Summary:
    {summary}

    Provide:
    - Explanation
    - Business impact
    - Actionable recommendations
    """

    return explain_insight(prompt)

