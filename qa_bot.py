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
            "- A small set of projects need immediate delivery attention.\n"
            "- Financial and people risks are emerging but still manageable.\n\n"
            "What I would focus on immediately:\n"
            "- Rebalance utilization across projects.\n"
            "- Stabilize high-risk deliveries.\n"
            "- Address cost and HR risks early before escalation."
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
            "- The following teams are operating below expected utilization levels.\n\n"
        )

        for _, r in low_teams.iterrows():
            response += (
                f"{r['department']} Team\n"
                "Why this is a concern:\n"
                f"- Average utilization is around {r['utilization_pct']:.1f}%.\n"
                "- Workload demand and staffing are misaligned.\n\n"
                "Why it matters:\n"
                "- Prolonged low utilization increases bench cost and inefficiency.\n\n"
                "Recommended action:\n"
                "- Reassign excess capacity to high-demand projects.\n"
                "- Upskill team members for billable roles.\n\n"
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
            "- These employees are currently underutilized and may be on bench.\n\n"
        )

        for _, r in low_emp.iterrows():
            response += (
                f"Employee {r['employee_id']}\n"
                "Why this is a concern:\n"
                f"- Utilization is approximately {r['utilization_pct']:.1f}%.\n"
                "- Limited billable allocation observed.\n\n"
                "Why it matters:\n"
                "- Sustained underutilization leads to cost leakage.\n\n"
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
        overstaffed = proj[
            (proj["employee_count"] >= 5) &
            (proj["avg_util"] < 100)
        ]

        if overstaffed.empty:
            return "At this point, I don’t see any projects that are clearly overstaffed."

        response = (
            "OVERSTAFFED PROJECTS\n\n"
            "Summary:\n"
            "- The following projects appear to have more capacity than required.\n\n"
        )

        for _, r in overstaffed.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- {r['employee_count']} resources assigned.\n"
                "- Average utilization per resource is low.\n\n"
                "Why it matters:\n"
                "- Overstaffing directly impacts margins and portfolio efficiency.\n\n"
                "Recommended action:\n"
                "- Reduce team size.\n"
                "- Reassign excess resources to high-demand projects.\n\n"
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
            "- These projects show elevated delivery risk indicators.\n\n"
        )

        for _, r in risky.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- {r['open_tickets']} open Jira tickets.\n"
                f"- {r['high_priority']} high-priority issues unresolved.\n\n"
                "Why it matters:\n"
                "- High-priority backlog often results in schedule slippage.\n\n"
                "Recommended action:\n"
                "- Freeze low-value scope.\n"
                "- Prioritize critical tickets.\n"
                "- Add senior resources until stability improves.\n\n"
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
            "- These projects are showing margin or cost risk.\n\n"
        )

        for _, r in loss.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- Project is running at a negative margin ({int(r['margin'])}).\n"
                f"- Cost overrun observed: {'Yes' if r['cost_overrun'] else 'No'}.\n\n"
                "Why it matters:\n"
                "- Continued margin erosion impacts overall portfolio profitability.\n\n"
                "Recommended action:\n"
                "- Review pricing and billing mix.\n"
                "- Control non-billable effort.\n"
                "- Rebalance team structure if needed.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 7️⃣ HR / ATTRITION RISK (PROFESSIONAL FORMAT)
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
            "- The following employees are showing early HR risk signals.\n"
            "- Primary drivers include attendance inconsistency and performance trends.\n\n"
        )

        for _, r in hr_risk.iterrows():
            response += (
                f"Employee {r['employee_id']}\n"
                "Why this is a concern:\n"
                f"- Attendance is trending below expectations ({r['avg_attendance']:.1f}%).\n"
                f"- Performance rating indicates potential disengagement ({r['avg_rating']:.1f}).\n\n"
                "Why it matters:\n"
                "- Unaddressed people risks often lead to attrition or productivity drops.\n"
                "- This can disrupt delivery continuity and team morale.\n\n"
                "Recommended action:\n"
                "- Manager-led discussion to understand concerns.\n"
                "- Clarify role expectations and growth path.\n"
                "- Monitor engagement over the next review cycle.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 8️⃣ FALLBACK (OPTIONAL LLM)
    # =========================================================
    llm_answer = explain_insight(question)
    return llm_answer or (
        "I can help with:\n"
        "- Utilization and bench analysis\n"
        "- Overstaffed or delivery-risk projects\n"
        "- Financial and margin risks\n"
        "- HR and attrition indicators\n"
        "- Executive delivery summaries"
    )
