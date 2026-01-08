from llm_groq import explain_insight

def answer_question(question, util_df, risk_df, cost_df, hr_df):
    context = f"""
    DATA SNAPSHOT:
    Underutilized Employees: {len(util_df[util_df.utilization_pct < 60])}
    Delivery Risk Projects: {len(risk_df[risk_df.risk_flag == 1])}
    Loss-Making Projects: {len(cost_df[cost_df.margin < 0])}
    HR Risk Employees: {len(hr_df[hr_df.hr_risk == 1])}
    """

    prompt = f"""
    User Question:
    {question}

    Context:
    {context}

    Respond with insights, business impact, and recommendations.
    """

    return explain_insight(prompt)
