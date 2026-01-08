import pandas as pd
from llm_groq import explain_insight


def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # =========================================================
    # 1️⃣ EXECUTIVE / OVERALL DELIVERY HEALTH
    # =========================================================
    if any(k in q for k in [
        "overall", "summary", "health",
        "leadership", "key insights", "major risks"
    ]):
        return (
            "OVERALL DELIVERY HEALTH SUMMARY\n\n"
            "Summary:\n"
            f"- Underutilized employees: {len(util_df[util_df['utilization_pct'] < 60])}\n"
            f"- Projects at delivery risk: {len(risk_df[risk_df['risk_flag'] == 1])}\n"
            f"- Projects with financial risk: {len(cost_df[cost_df['margin'] < 0])}\n"
            f"- Employees with HR risk signals: {len(hr_df[hr_df['hr_risk'] == 1])}\n\n"
            "What this tells me:\n"
            "- We have bench inefficiencies impacting cost.\n"
            "- A few projects need immediate delivery stabilization.\n"
            "- Early people risks are visible but still manageable.\n\n"
            "What I would focus on immediately:\n"
            "- Rebalance utilization across projects.\n"
            "- Contain delivery risk before it escalates.\n"
            "- Address cost and HR risks early."
        )

    # =========================================================
    # 2️⃣ TEAM / DEPARTMENT UTILIZATION
    # =========================================================
    if "team" in q or "department" in q:
        team_util = (
            data.groupby("department")["hours_logged"]
            .sum()
            .reset_index()
        )
        team_util["utilization_pct"] = (team_util["hours_logged"] / 160) * 100
        low_teams = team_util.sort_values("utilization_pct").head(3)

        response = (
            "TEAMS WITH LOW UTILIZATION\n\n"
            "Summary:\n"
            "- These teams are operating below expected utilization levels.\n\n"
        )

        for _, r in low_teams.iterrows():
            response += (
                f"{r['department']} Team\n"
                "Why this is a concern:\n"
                f"- Average utilization is {r['utilization_pct']:.1f}%.\n"
                "- Demand and staffing are misaligned.\n\n"
                "Why it matters:\n"
                "- Sustained low utilization increases bench cost.\n\n"
                "Recommended action:\n"
                "- Reassign excess capacity to high-demand projects.\n"
                "- Upskill team members for billable work.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 3️⃣ EMPLOYEE UTILIZATION / BENCH
    # =========================================================
    if any(k in q for k in [
        "utilization", "bench", "underutilized",
        "not fully utilized"
    ]):
        low_emp = util_df[util_df["utilization_pct"] < 60] \
            .sort_values("utilization_pct") \
            .head(5)

        response = (
            "UNDERUTILIZED EMPLOYEES\n\n"
            "Summary:\n"
            "- These employees are currently underutilized.\n\n"
        )

        for _, r in low_emp.iterrows():
            response += (
                f"Employee {r['employee_id']}\n"
                "Why this is a concern:\n"
                f"- Utilization is {r['utilization_pct']:.1f}%.\n\n"
                "Why it matters:\n"
                "- Prolonged bench time leads to cost leakage.\n\n"
                "Recommended action:\n"
                "- Assign to active or upcoming projects.\n"
                "- Ensure ownership of billable deliverables.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 4️⃣ OVERSTAFFED PROJECTS
    # =========================================================
    if any(k in q for k in [
        "overstaffed", "too many people",
        "over staffed", "staffed heavily"
    ]):
        proj = (
            data.groupby("project_id")
            .agg(
                employee_count=("employee_id", "nunique"),
                total_hours=("hours_logged", "sum")
            )
            .reset_index()
        )
        proj["avg_util"] = proj["total_hours"] / proj["employee_count"]
        overstaffed = proj[(proj["employee_count"] >= 5) & (proj["avg_util"] < 100)]

        if overstaffed.empty:
            return "At this point, I don’t see any projects that are clearly overstaffed."

        response = (
            "OVERSTAFFED PROJECTS\n\n"
            "Summary:\n"
            "- These projects have more capacity than required.\n\n"
        )

        for _, r in overstaffed.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- {r['employee_count']} resources assigned.\n"
                "- Average utilization per resource is low.\n\n"
                "Why it matters:\n"
                "- Overstaffing directly impacts margins.\n\n"
                "Recommended action:\n"
                "- Reduce team size.\n"
                "- Redeploy excess resources.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 5️⃣ DELIVERY RISK / PROJECT HEALTH
    # =========================================================
    if any(k in q for k in [
        "delivery risk", "risk", "delay",
        "delivery problems", "miss deadlines"
    ]):
        risky = risk_df[risk_df["risk_flag"] == 1].head(3)

        response = (
            "PROJECTS AT DELIVERY RISK\n\n"
            "Summary:\n"
            "- These projects show elevated delivery risk.\n\n"
        )

        for _, r in risky.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- {r['open_tickets']} open Jira tickets.\n"
                f"- {r['high_priority']} high-priority issues.\n\n"
                "Why it matters:\n"
                "- High-priority backlog typically leads to schedule slippage.\n\n"
                "Recommended action:\n"
                "- Freeze low-value scope.\n"
                "- Prioritize critical tickets.\n"
                "- Add senior resources temporarily.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 6️⃣ FINANCIAL / MARGIN RISK
    # =========================================================
    if any(k in q for k in [
        "cost", "margin", "loss", "financial",
        "budget", "profit", "financial review",
        "losing money"
    ]):
        loss = cost_df[cost_df["margin"] < 0].head(3)

        response = (
            "PROJECTS NEEDING FINANCIAL REVIEW\n\n"
            "Summary:\n"
            "- These projects show margin or cost risk.\n\n"
        )

        for _, r in loss.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- Negative margin ({int(r['margin'])}).\n"
                f"- Cost overrun: {'Yes' if r['cost_overrun'] else 'No'}.\n\n"
                "Why it matters:\n"
                "- Continued erosion impacts portfolio profitability.\n\n"
                "Recommended action:\n"
                "- Review pricing and billing mix.\n"
                "- Reduce non-billable effort.\n"
                "- Rebalance team structure.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 7️⃣ HR / ATTRITION RISK (CUSTOMIZED PER EMPLOYEE)
    # =========================================================
    if any(k in q for k in [
        "hr", "attendance", "attrition",
        "people", "performance", "leave"
    ]):
        hr_risk = hr_df[hr_df["hr_risk"] == 1].head(3)

        if hr_risk.empty:
            return "At this point, I do not see any employees with significant HR risk signals."

        response = (
            "EMPLOYEES WITH HR RISK INDICATORS\n\n"
            "Summary:\n"
            "- These employees show people-risk signals based on attendance and performance trends.\n\n"
        )

        for _, r in hr_risk.iterrows():
            attendance = r["avg_attendance"]
            rating = r["avg_rating"]

            if attendance < 85 and rating < 3.5:
                why_matters = (
                    "This combination indicates disengagement and a high probability of attrition "
                    "if not addressed promptly."
                )
                recommendation = (
                    "- Immediate manager-led intervention.\n"
                    "- HRBP involvement for retention planning.\n"
                    "- Review role fit, workload, and growth path."
                )

            elif attendance < 85 and rating >= 3.5:
                why_matters = (
                    "Performance remains strong, but attendance patterns suggest burnout or "
                    "personal constraints rather than disengagement."
                )
                recommendation = (
                    "- Manager check-in focused on well-being.\n"
                    "- Adjust workload or provide flexibility.\n"
                    "- Monitor attendance trend before escalation."
                )

            elif attendance >= 85 and rating < 3.5:
                why_matters = (
                    "Attendance is stable, but performance trends suggest skill gaps or role misalignment."
                )
                recommendation = (
                    "- Targeted coaching or training.\n"
                    "- Clarify role expectations.\n"
                    "- Set short-term improvement goals."
                )

            else:
                why_matters = (
                    "Signals are mild but worth monitoring to prevent future disengagement."
                )
                recommendation = (
                    "- Light-touch manager conversation.\n"
                    "- Continue regular performance check-ins."
                )

            response += (
                f"Employee {r['employee_id']}\n"
                "Why this is a concern:\n"
                f"- Attendance average: {attendance:.1f}%.\n"
                f"- Performance rating: {rating:.1f}.\n\n"
                "Why it matters:\n"
                f"- {why_matters}\n\n"
                "Recommended action:\n"
                f"{recommendation}\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 8️⃣ FALLBACK (OPTIONAL LLM)
    # =========================================================
    llm_answer = explain_insight(question)
    return llm_answer or (
        "I can help with utilization, delivery risk, financial health, "
        "overstaffing, HR risk, and executive delivery summaries."
    )
