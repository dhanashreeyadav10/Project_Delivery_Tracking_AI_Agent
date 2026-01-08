from llm_groq import explain_insight


def answer_question(question, util_df, risk_df, cost_df, hr_df):
    # ---------------- PREPARE CONTEXT ----------------
    context = f"""
    DATA SNAPSHOT:

    Underutilized Employees (<60%): {len(util_df[util_df.utilization_pct < 60])}
    Delivery Risk Projects: {len(risk_df[risk_df.risk_flag == 1])}
    Loss-Making Projects: {len(cost_df[cost_df.margin < 0])}
    HR Risk Employees (Attrition Signals): {len(hr_df[hr_df.hr_risk == 1])}

    Definitions:
    - HR Risk = Low attendance (<90%) or low performance rating (<3.5)
    - Delivery Risk = Too many open or high-priority Jira tickets
    """

    prompt = f"""
    You are analyzing enterprise delivery and workforce data.

    User Question:
    "{question}"

    Context:
    {context}

    Respond with:
    1. Direct answer
    2. Business impact
    3. Recommended actions
    """

    # ---------------- ALWAYS CALL LLM ----------------
    return explain_insight(prompt)
