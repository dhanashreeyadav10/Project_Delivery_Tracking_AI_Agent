# from llm_groq import explain_insight

# def answer_question(question, util_df, risk_df, leakage_df):
#     """
#     Answers natural language questions based on delivery analytics.
#     Uses uploaded data only.
#     """

#     q = question.lower()

#     # -------------------------------
#     # Intent Detection
#     # -------------------------------
#     if "underutil" in q or "low utilization" in q or "bench" in q:
#         data = util_df[util_df["utilization"] < 0.6]
#         summary = f"{len(data)} employees are underutilized."
#         context = data.head(10).to_string(index=False)

#     elif "risk" in q or "delay" in q:
#         data = risk_df[risk_df["risk"] == 1]
#         summary = f"{len(data)} projects are at risk of delay."
#         context = data.to_string(index=False)

#     elif "billing" in q or "leakage" in q or "revenue" in q:
#         data = leakage_df
#         summary = f"{len(data)} records indicate billing leakage."
#         context = data.head(10).to_string(index=False)

#     elif "summary" in q or "overview" in q or "health" in q:
#         summary = "Overall project delivery health overview."
#         context = f"""
#         Underutilized Employees: {len(util_df[util_df['utilization'] < 0.6])}
#         Risky Projects: {len(risk_df[risk_df['risk'] == 1])}
#         Billing Leakage Records: {len(leakage_df)}
#         """

#     else:
#         summary = "General delivery analytics insight."
#         context = f"""
#         Utilization rows: {len(util_df)}
#         Risk rows: {len(risk_df)}
#         Leakage rows: {len(leakage_df)}
#         """

#     # -------------------------------
#     # LLM Prompt
#     # -------------------------------
#     prompt = f"""
#     You are an enterprise Project & Delivery Analytics Advisor.

#     User Question:
#     {question}

#     Key Findings:
#     {summary}

#     Data Context:
#     {context}

#     Provide:
#     - Clear explanation
#     - Business impact
#     - Actionable recommendations
#     """

#     response = explain_insight(prompt)
#     return response



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
