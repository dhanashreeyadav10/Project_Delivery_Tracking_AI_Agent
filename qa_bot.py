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
            f"Overall Delivery Health Summary:\n\n"
            f"- Underutilized Employees: {len(util_df[util_df['utilization_pct'] < 60])}\n"
            f"- Delivery Risk Projects: {len(risk_df[risk_df['risk_flag'] == 1])}\n"
            f"- Loss-Making Projects: {len(cost_df[cost_df['margin'] < 0])}\n"
            f"- HR Risk Employees: {len(hr_df[hr_df['hr_risk'] == 1])}\n\n"
            "Leadership Focus Areas:\n"
            "- Improve bench utilization\n"
            "- Mitigate delivery risks\n"
            "- Address margin leakage\n"
            "- Engage HR on risk signals"
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

        response = "Teams with Low Utilization:\n\n"
        for _, r in low_teams.iterrows():
            response += f"- {r['department']} | {r['utilization_pct']:.1f}% utilization\n"

        return response

    # =========================================================
    # 3️⃣ EMPLOYEE UTILIZATION / BENCH
    # =========================================================
    if any(k in q for k in [
        "utilization", "bench", "underutilized",
        "under utilized", "not fully utilized"
    ]):
        low_emp = util_df[util_df["utilization_pct"] < 60]

        if low_emp.empty:
            return "No underutilized employees found."

        response = "Underutilized Employees (Top 10):\n\n"
        for _, r in low_emp.sort_values("utilization_pct").head(10).iterrows():
            response += f"- {r['employee_id']} | {r['utilization_pct']:.1f}% utilization\n"

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

        if overstaffed.empty:
            return "No overstaffed projects identified."

        response = "Overstaffed Projects (Low Utilization):\n\n"
        for _, r in overstaffed.iterrows():
            response += (
                f"- Project {r['project_id']} | "
                f"Employees: {r['employee_count']} | "
                f"Avg Utilization: {r['avg_utilization']:.1f}\n"
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

        if risky.empty:
            return "No delivery risk projects identified."

        response = "Projects at Delivery Risk:\n\n"
        for _, r in risky.iterrows():
            response += (
                f"- Project {r['project_id']} | "
                f"Open Tickets: {r['open_tickets']} | "
                f"High Priority: {r['high_priority']}\n"
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

        if loss.empty:
            return "No projects currently require financial review."

        response = "Projects Needing Financial Review:\n\n"
        for _, r in loss.iterrows():
            response += (
                f"- Project {r['project_id']} | "
                f"Margin: {int(r['margin'])} | "
                f"Cost Overrun: {'Yes' if r['cost_overrun'] else 'No'}\n"
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

        if hr_risk.empty:
            return "No HR risk employees identified."

        response = "Employees with HR Risk Indicators:\n\n"
        for _, r in hr_risk.iterrows():
            response += (
                f"- {r['employee_id']} | "
                f"Attendance: {r['avg_attendance']:.1f}% | "
                f"Rating: {r['avg_rating']:.1f}\n"
            )

        return response

    # =========================================================
    # 8️⃣ FALLBACK (OPTIONAL LLM)
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
