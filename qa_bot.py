from llm_groq import explain_insight

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # ---------------- UTILIZATION ----------------
    if any(k in q for k in ["utilization", "bench", "idle"]):
        data = util_df[util_df["utilization_pct"] < 60]
        summary = f"{len(data)} employees are underutilized."

    # ---------------- DELIVERY RISK ----------------
    elif any(k in q for k in ["risk", "delay", "jira"]):
        data = risk_df[risk_df["risk_flag"] == 1]
        summary = f"{len(data)} projects are at delivery risk."

    # ---------------- COST / MARGIN ----------------
    elif any(k in q for k in ["cost", "margin", "loss"]):
        data = cost_df[cost_df["margin"] < 0]
        summary = f"{len(data)} projects are loss-making."

    # ---------------- ATTRITION / HR ----------------
    elif any(k in q for k in ["leave", "attrition", "exit", "resign", "hr"]):
        data = hr_df[hr_df["hr_risk"] == 1]
        summary = (
            f"{len(data)} employees show attrition risk indicators "
            "(low attendance or poor performance)."
        )

    else:
        summary = "Overall enterprise delivery and workforce health."
        data = None

    prompt = f"""
    You are an enterprise HR & delivery intelligence advisor.

    User Question:
    {question}

    Data Insight:
    {summary}

    Explain:
    - Why this is happening
    - Business impact
    - What leadership should do next
    """

    return explain_insight(prompt)
