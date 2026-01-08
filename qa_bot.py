import pandas as pd
from llm_groq import explain_insight


STANDARD_MONTHLY_CAPACITY = 160  # hours per employee


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
            f"- Underutilized employees (<60%): {len(util_df[util_df['utilization_pct'] < 60])}\n"
            f"- Projects at delivery risk: {len(risk_df[risk_df['risk_flag'] == 1])}\n"
            f"- Projects with financial risk: {len(cost_df[cost_df['margin'] < 0])}\n"
            f"- Employees with HR risk signals: {len(hr_df[hr_df['hr_risk'] == 1])}\n\n"
            "What this tells me:\n"
            "- There is bench inefficiency impacting cost.\n"
            "- A subset of projects need delivery stabilization.\n"
            "- People risks are emerging but still actionable.\n\n"
            "Immediate focus:\n"
            "- Rebalance utilization.\n"
            "- Stabilize risky projects.\n"
            "- Address HR and financial risks early."
        )

    # =========================================================
    # 2️⃣ TEAM / DEPARTMENT UTILIZATION (FIXED LOGIC)
    # =========================================================
    if "team" in q or "department" in q:
        team_util = (
            data.groupby("department")
            .agg(
                total_hours=("hours_logged", "sum"),
                employee_count=("employee_id", "nunique")
            )
            .reset_index()
        )

        team_util["utilization_pct"] = (
            team_util["total_hours"] /
            (team_util["employee_count"] * STANDARD_MONTHLY_CAPACITY)
        ) * 100

        team_util["utilization_pct"] = team_util["utilization_pct"].clip(upper=100)
        low_teams = team_util.sort_values("utilization_pct").head(3)

        response = (
            "TEAMS WITH LOW UTILIZATION\n\n"
            "Summary:\n"
            "- These teams are operating below optimal utilization levels.\n\n"
        )

        for _, r in low_teams.iterrows():
            response += (
                f"{r['department']} Team\n"
                "Why this is a concern:\n"
                f"- Average utilization is {r['utilization_pct']:.1f}%.\n"
                "- Available capacity is not fully leveraged.\n\n"
                "Why it matters:\n"
                "- Sustained low utilization increases bench cost.\n\n"
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
            "- These employees are currently underutilized.\n\n"
        )

        for _, r in low_emp.iterrows():
            response += (
                f"Employee {r['employee_id']}\n"
                "Why this is a concern:\n"
                f"- Utilization is {r['utilization_pct']:.1f}%.\n\n"
                "Why it matters:\n"
                "- Extended bench time directly impacts delivery cost efficiency.\n\n"
                "Recommended action:\n"
                "- Assign to active or upcoming work.\n"
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

        proj["avg_util"] = (
            proj["total_hours"] /
            (proj["employee_count"] * STANDARD_MONTHLY_CAPACITY)
        ) * 100

        overstaffed = proj[
            (proj["employee_count"] >= 5) &
            (proj["avg_util"] < 60)
        ]

        if overstaffed.empty:
            return "At this point, I don’t see any projects that are clearly overstaffed."

        response = (
            "OVERSTAFFED PROJECTS\n\n"
            "Summary:\n"
            "- These projects appear to have excess capacity.\n\n"
        )

        for _, r in overstaffed.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- Team utilization is only {r['avg_util']:.1f}%.\n"
                f"- {r['employee_count']} resources assigned.\n\n"
                "Why it matters:\n"
                "- Overstaffing reduces margins and portfolio efficiency.\n\n"
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
            "- These projects show elevated delivery risk indicators.\n\n"
        )

        for _, r in risky.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- {r['open_tickets']} open Jira tickets.\n"
                f"- {r['high_priority']} high-priority issues.\n\n"
                "Why it matters:\n"
                "- High-priority backlog often leads to schedule slippage.\n\n"
                "Recommended action:\n"
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
        "budget", "profit", "financial review"
    ]):
        loss = cost_df[cost_df["margin"] < 0].head(3)

        response = (
            "PROJECTS NEEDING FINANCIAL REVIEW\n\n"
            "Summary:\n"
            "- These projects are running at financial risk.\n\n"
        )

        for _, r in loss.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                "Why this is a concern:\n"
                f"- Negative margin of {int(r['margin'])}.\n\n"
                "Why it matters:\n"
                "- Continued losses impact portfolio profitability.\n\n"
                "Recommended action:\n"
                "- Review pricing and billing mix.\n"
                "- Reduce non-billable effort.\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 7️⃣ HR / ATTRITION RISK (CUSTOMIZED)
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
            "- The following employees show early people-risk signals.\n\n"
        )

        for _, r in hr_risk.iterrows():
            attendance = r["avg_attendance"]
            rating = r["avg_rating"]

            if attendance < 85 and rating < 3.5:
                why = "High attrition risk due to disengagement."
                action = (
                    "- Immediate manager + HRBP intervention.\n"
                    "- Role and growth-path reassessment."
                )
            elif attendance < 85:
                why = "Potential burnout or personal constraints."
                action = (
                    "- Workload adjustment.\n"
                    "- Flexible scheduling."
                )
            else:
                why = "Skill or role misalignment risk."
                action = (
                    "- Targeted coaching.\n"
                    "- Short-term performance goals."
                )

            response += (
                f"Employee {r['employee_id']}\n"
                f"- Attendance: {attendance:.1f}%\n"
                f"- Performance rating: {rating:.1f}\n\n"
                "Why it matters:\n"
                f"- {why}\n\n"
                "Recommended action:\n"
                f"{action}\n\n"
                "--------------------------------------------\n\n"
            )

        return response.strip()

    # =========================================================
    # 8️⃣ FALLBACK
    # =========================================================
    llm_answer = explain_insight(question)
    return llm_answer or (
        "I can help with utilization, delivery risk, financial health, "
        "overstaffing, HR risk, and executive delivery summaries."
    )
