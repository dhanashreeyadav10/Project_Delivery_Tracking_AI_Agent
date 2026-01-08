from llm_groq import explain_insight


def answer_question(question, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    if "util" in q:
        summary = f"{len(util_df[util_df.utilization_pct < 60])} underutilized employees."
    elif "risk" in q:
        summary = f"{len(risk_df[risk_df.risk_flag == 1])} risky projects."
    elif "cost" in q or "margin" in q:
        summary = f"{len(cost_df[cost_df.margin < 0])} loss-making projects."
    elif "hr" in q:
        summary = f"{len(hr_df[hr_df.hr_risk == 1])} HR risk employees."
    else:
        summary = "Overall enterprise delivery health."

    return explain_insight(
        f"Question: {question}\nSummary: {summary}\nProvide insights and actions."
    )
