import pandas as pd
from llm_groq import explain_insight


def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # =========================================================
    # EXECUTIVE / OVERALL HEALTH
    # =========================================================
    if any(k in q for k in [
        "overall", "summary", "health",
        "leadership", "key insights", "major risks"
    ]):
        return (
            "From an overall delivery standpoint, here’s how things look right now.\n\n"
            f"We currently have {len(util_df[util_df['utilization_pct'] < 60])} underutilized employees, "
            f"{len(risk_df[risk_df['risk_flag'] == 1])} projects showing delivery risk, "
            f"{len(cost_df[cost_df['margin'] < 0])} projects with financial concerns, "
            f"and {len(hr_df[hr_df['hr_risk'] == 1])} employees showing HR risk signals.\n\n"
            "What this tells me is that we have a combination of bench inefficiency, "
            "delivery pressure on a few projects, and early people-risk indicators.\n\n"
            "My immediate focus would be to rebalance utilization, stabilize risky deliveries, "
            "and intervene early on cost and HR signals before they escalate."
        )

    # =========================================================
    # TEAM / DEPARTMENT UTILIZATION
    # =========================================================
    if "team" in q or "department" in q:
        team_util = (
            data.groupby("department")["hours_logged"]
            .sum()
            .reset_index()
        )
        team_util["utilization_pct"] = (team_util["hours_logged"] / 160) * 100
        low_teams = team_util.sort_values("utilization_pct").head(3)

        response = ""
        for _, r in low_teams.iterrows():
            response += (
                f"{r['department']} team is currently underutilized.\n\n"
                f"What I’m seeing is an average utilization of about {r['utilization_pct']:.1f}%, "
                "which suggests that demand and staffing are not aligned.\n\n"
                "Why this matters is that prolonged low utilization directly impacts cost efficiency "
                "and increases bench risk.\n\n"
                "What I would do next is reassign excess capacity to high-demand projects "
                "or reskill the team towards billable work.\n\n"
            )
        return response.strip()

    # =========================================================
    # EMPLOYEE UTILIZATION / BENCH
    # =========================================================
    if any(k in q for k in [
        "utilization", "bench", "underutilized",
        "not fully utilized"
    ]):
        low_emp = util_df[util_df["utilization_pct"] < 60].sort_values("utilization_pct").head(5)

        response = ""
        for _, r in low_emp.iterrows():
            response += (
                f"Employee {r['employee_id']} is currently underutilized.\n\n"
                f"They are operating at roughly {r['utilization_pct']:.1f}% utilization, "
                "which indicates limited billable allocation.\n\n"
                "From a delivery perspective, this is a bench leakage risk if it continues.\n\n"
                "I would look to place this resource onto an active project "
                "or assign ownership of billable deliverables immediately.\n\n"
            )
        return response.strip()

    # =========================================================
    # OVERSTAFFED PROJECTS
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

        response = ""
        for _, r in overstaffed.iterrows():
            response += (
                f"Project {r['project_id']} appears overstaffed.\n\n"
                f"We have {r['employee_count']} people assigned, "
                f"but average utilization per person is relatively low.\n\n"
                "This tells me we are carrying more capacity than the workload justifies.\n\n"
                "I would reduce the team size and redeploy excess resources "
                "to projects that are under delivery pressure.\n\n"
            )
        return response.strip()

    # =========================================================
    # DELIVERY RISK / PROJECT HEALTH
    # =========================================================
    if any(k in q for k in [
        "delivery risk", "risk", "delay",
        "delivery problems", "miss deadlines"
    ]):
        risky = risk_df[risk_df["risk_flag"] == 1]

        response = ""
        for _, r in risky.iterrows():
            response += (
                f"Project {r['project_id']} is at delivery risk.\n\n"
                f"We currently have {r['open_tickets']} open Jira tickets, "
                f"with {r['high_priority']} of them marked high priority.\n\n"
                "From experience, this level of unresolved high-priority work "
                "usually results in schedule slippage.\n\n"
                "My next step would be to freeze low-value scope, "
                "prioritize critical tickets, and add senior resources "
                "until stability is restored.\n\n"
            )
        return response.strip()

    # =========================================================
    # FINANCIAL / MARGIN
    # =========================================================
    if any(k in q for k in [
        "cost", "margin", "loss", "financial",
        "budget", "profit", "financial review",
        "losing money"
    ]):
        loss = cost_df[cost_df["margin"] < 0]

        response = ""
        for _, r in loss.iterrows():
            response += (
                f"Project {r['project_id']} needs financial attention.\n\n"
                f"The project is running at a negative margin of {int(r['margin'])}, "
                "which indicates cost leakage.\n\n"
                "This usually happens when delivery effort exceeds what we can bill.\n\n"
                "I would immediately review pricing, billing mix, "
                "and team structure to stop further margin erosion.\n\n"
            )
        return response.strip()

    # =========================================================
    # HR / ATTRITION
    # =========================================================
    if any(k in q for k in [
        "hr", "attendance", "attrition",
        "people", "performance", "leave"
    ]):
        hr_risk = hr_df[hr_df["hr_risk"] == 1]

        response = ""
        for _, r in hr_risk.iterrows():
            response += (
                f"Employee {r['employee_id']} is showing early HR risk signals.\n\n"
                f"Their attendance and performance trends suggest disengagement.\n\n"
                "From a delivery standpoint, unresolved people risks "
                "often lead to attrition or productivity drops.\n\n"
                "I would recommend a manager-led discussion to understand concerns "
                "and realign expectations early.\n\n"
            )
        return response.strip()

    # =========================================================
    # FALLBACK (OPTIONAL LLM)
    # =========================================================
    llm_answer = explain_insight(question)
    return llm_answer or (
        "I can help assess utilization, delivery risk, financial health, "
        "overstaffing, and HR concerns across the portfolio."
    )
