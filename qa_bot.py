from llm_groq import explain_insight

def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # ------------------------------------------------
    # TEAM / DEPARTMENT UTILIZATION
    # ------------------------------------------------
    if "team" in q or "department" in q:
        team_util = (
            data.groupby("department")["hours_logged"]
            .sum()
            .reset_index()
        )
        team_util["utilization_pct"] = (team_util["hours_logged"] / 160) * 100

        low_teams = team_util.sort_values("utilization_pct").head(5)

        response = "Teams with Low Utilization:\n\n"
        for _, r in low_teams.iterrows():
            response += f"- {r['department']} | {r['utilization_pct']:.1f}% utilization\n"

        return response

    # ------------------------------------------------
    # EMPLOYEE UTILIZATION
    # ------------------------------------------------
    if any(k in q for k in ["utilization", "bench", "underutilized", "under utilized"]):
        low_emp = util_df[util_df["utilization_pct"] < 60]

        response = "Underutilized Employees (Top 10):\n\n"
        for _, r in low_emp.sort_values("utilization_pct").head(10).iterrows():
            response += f"- {r['employee_id']} | {r['utilization_pct']:.1f}% utilization\n"

        return response

    # ------------------------------------------------
    # DELIVERY RISK / PROJECT HEALTH
    # ------------------------------------------------
    if any(k in q for k in ["delivery risk", "risk", "delay", "at risk"]):
        risky = risk_df[risk_df["risk_flag"] == 1]

        response = "Projects with Delivery Risk:\n\n"
        for _, r in risky.iterrows():
            response += (
                f"- Project {r['project_id']} "
                f"(Open Tickets: {r['open_tickets']}, "
                f"High Priority: {r['high_priority']})\n"
            )

        return response

    # ------------------------------------------------
    # FINANCIAL / COST / MARGIN / REVIEW
    # ------------------------------------------------
    if any(k in q for k in [
        "cost", "margin", "loss",
        "financial", "finance",
        "budget", "profit",
        "review", "overrun"
    ]):
        loss = cost_df[cost_df["margin"] < 0]

        if loss.empty:
            return "No projects currently require financial review."

        response = "Projects Needing Financial Review:\n\n"
        for _, r in loss.iterrows():
            response += (
                f"- Project {r['project_id']} "
                f"| Margin: {int(r['margin'])} "
                f"| Cost Overrun: {'Yes' if r['cost_overrun'] else 'No'}\n"
            )

        return response

    # ------------------------------------------------
    # HR / ATTRITION / ATTENDANCE
    # ------------------------------------------------
    if any(k in q for k in ["hr", "attendance", "attrition", "people risk"]):
        hr_risk = hr_df[hr_df["hr_risk"] == 1]

        response = "Employees with HR Risk Indicators:\n\n"
        for _, r in hr_risk.iterrows():
            response += (
                f"- {r['employee_id']} "
                f"| Attendance: {r['avg_attendance']:.1f}% "
                f"| Rating: {r['avg_rating']:.1f}\n"
            )

        return response

    # ------------------------------------------------
    # FALLBACK (OPTIONAL LLM)
    # ------------------------------------------------
    llm_answer = explain_insight(question)
    return llm_answer or (
        "I can help with:\n"
        "- Team or employee utilization\n"
        "- Delivery risk projects\n"
        "- Financial / margin review\n"
        "- HR risk indicators"
    )
