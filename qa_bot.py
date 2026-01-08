from llm_groq import explain_insight
import pandas as pd

def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # =========================================================
    # 1️⃣ EXECUTIVE / OVERALL SUMMARY
    # =========================================================
    if any(k in q for k in [
        "overall", "summary", "key insights",
        "leadership", "major risks", "health"
    ]):
        return (
            "OVERALL DELIVERY HEALTH SUMMARY\n\n"
            f"Underutilized Employees: {len(util_df[util_df['utilization_pct'] < 60])}\n"
            f"Delivery Risk Projects: {len(risk_df[risk_df['risk_flag'] == 1])}\n"
            f"Loss-Making Projects: {len(cost_df[cost_df['margin'] < 0])}\n"
            f"HR Risk Employees: {len(hr_df[hr_df['hr_risk'] == 1])}\n\n"
            "WHY:\n"
            "- Bench utilization inefficiencies\n"
            "- High-priority unresolved Jira tickets\n"
            "- Cost overruns and pricing gaps\n"
            "- Attendance and performance dips\n\n"
            "RECOMMENDATIONS:\n"
            "- Reallocate underutilized resources\n"
            "- Fast-track critical delivery issues\n"
            "- Review pricing and cost controls\n"
            "- Proactively engage HR on risk signals"
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

        low_teams = team_util.sort_values("utilization_pct").head(5)

        response = "TEAMS WITH LOW UTILIZATION\n\n"
        for _, r in low_teams.iterrows():
            response += (
                f"{r['department']}\n"
                f"WHY:\n"
                f"- Average utilization is only {r['utilization_pct']:.1f}%\n"
                f"- Low billable workload\n\n"
                f"RECOMMENDATION:\n"
                f"- Reassign resources to high-demand projects\n"
                f"- Upskill team for billable roles\n\n"
            )

        return response

    # =========================================================
    # 3️⃣ EMPLOYEE UTILIZATION / BENCH
    # =========================================================
    if any(k in q for k in [
        "utilization", "bench", "underutilized",
        "under utilized", "not fully utilized"
    ]):
        low_emp = util_df[util_df["utilization_pct"] < 60].sort_values("utilization_pct").head(5)

        response = "UNDERUTILIZED EMPLOYEES\n\n"
        for _, r in low_emp.iterrows():
            response += (
                f"Employee {r['employee_id']}\n"
                f"WHY:\n"
                f"- Utilization is only {r['utilization_pct']:.1f}%\n"
                f"- Limited billable task allocation\n\n"
                f"RECOMMENDATION:\n"
                f"- Allocate to active projects\n"
                f"- Assign billable responsibilities\n\n"
            )

        return response

    # =========================================================
    # 4️⃣ OVERSTAFFED PROJECTS
    # =========================================================
    if any(k in q for k in [
        "overstaffed", "too many people",
        "over staffed", "staffed heavily"
    ]):
        proj_util = (
            data.groupby("project_id")
            .agg(
                employee_count=("employee_id", "nunique"),
                total_hours=("hours_logged", "sum")
            )
            .reset_index()
        )

        proj_util["avg_utilization"] = proj_util["total_hours"] / proj_util["employee_count"]

        overstaffed = proj_util[
            (proj_util["employee_count"] >= 5) &
            (proj_util["avg_utilization"] < 100)
        ]

        response = "OVERSTAFFED PROJECTS\n\n"
        for _, r in overstaffed.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                f"WHY:\n"
                f"- {r['employee_count']} employees assigned\n"
                f"- Average utilization per employee is low ({r['avg_utilization']:.1f})\n\n"
                f"RECOMMENDATION:\n"
                f"- Reduce team size\n"
                f"- Reassign excess resources\n\n"
            )

        return response

    # =========================================================
    # 5️⃣ DELIVERY RISK / PROJECT HEALTH
    # =========================================================
    if any(k in q for k in [
        "delivery risk", "risk", "delay",
        "miss deadlines", "delivery problems"
    ]):
        risky = risk_df[risk_df["risk_flag"] == 1]

        response = "PROJECTS AT DELIVERY RISK\n\n"
        for _, r in risky.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                f"WHY:\n"
                f"- {r['open_tickets']} open Jira tickets\n"
                f"- {r['high_priority']} high-priority issues\n\n"
                f"RECOMMENDATION:\n"
                f"- Prioritize critical tickets\n"
                f"- Add experienced resources\n\n"
            )

        return response

    # =========================================================
    # 6️⃣ FINANCIAL / MARGIN / COST
    # =========================================================
    if any(k in q for k in [
        "cost", "margin", "loss", "profit",
        "financial", "budget", "overrun",
        "losing money", "financial review"
    ]):
        loss = cost_df[cost_df["margin"] < 0]

        response = "PROJECTS NEEDING FINANCIAL REVIEW\n\n"
        for _, r in loss.iterrows():
            response += (
                f"Project {r['project_id']}\n"
                f"WHY:\n"
                f"- Negative margin ({int(r['margin'])})\n"
                f"- Cost overrun: {'Yes' if r['cost_overrun'] else 'No'}\n\n"
                f"RECOMMENDATION:\n"
                f"- Review billing rates\n"
                f"- Control delivery costs\n"
                f"- Improve billable utilization\n\n"
            )

        return response

    # =========================================================
    # 7️⃣ HR / ATTRITION / PEOPLE RISK
    # =========================================================
    if any(k in q for k in [
        "hr", "attendance", "attrition",
        "people", "leave", "performance"
    ]):
        hr_risk = hr_df[hr_df["hr_risk"] == 1]

        response = "EMPLOYEES WITH HR RISK\n\n"
        for _, r in hr_risk.iterrows():
            response += (
                f"Employee {r['employee_id']}\n"
                f"WHY:\n"
                f"- Attendance below threshold ({r['avg_attendance']:.1f}%)\n"
                f"- Performance rating is low ({r['avg_rating']:.1f})\n\n"
                f"RECOMMENDATION:\n"
                f"- Manager intervention\n"
                f"- Career or role discussion\n\n"
            )

        return response

    # =========================================================
    # 8️⃣ FALLBACK
    # =========================================================
    llm_answer = explain_insight(question)
    return llm_answer or (
        "I can help with:\n"
        "- Utilization & bench analysis\n"
        "- Overstaffed or risky projects\n"
        "- Financial / margin risks\n"
        "- HR & attrition indicators\n"
        "- Executive summaries"
    )
