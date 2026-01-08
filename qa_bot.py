import pandas as pd
from llm_groq import explain_insight

STANDARD_MONTHLY_CAPACITY = 160


def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower().strip()

    # =========================================================
    # 🔴 PRIORITY 1 — ATTRITION / LIKELY TO LEAVE (OVERRIDE ALL)
    # =========================================================
    if any(k in q for k in [
        "likely to leave", "attrition", "people leave",
        "resign", "quit", "leave the company"
    ]):
        risky = hr_df[hr_df["hr_risk"] == 1]

        if risky.empty:
            return (
                "ATTRITION RISK ASSESSMENT\n\n"
                "Based on current attendance and performance indicators, "
                "I do not see any employees showing strong attrition risk signals at this time."
            )

        # Safe employee lookup table
        emp_lookup = (
            data[["employee_id", "employee_name", "department"]]
            .drop_duplicates()
            .set_index("employee_id")
        )

        rows = []
        for _, r in risky.iterrows():
            emp_id = r["employee_id"]

            if emp_id not in emp_lookup.index:
                continue

            emp = emp_lookup.loc[emp_id]

            rows.append({
                "employee_id": emp_id,
                "employee_name": emp["employee_name"],
                "team": emp["department"],
                "attendance": round(r["avg_attendance"], 1),
                "performance_rating": round(r["avg_rating"], 1)
            })

        if not rows:
            return (
                "ATTRITION RISK ASSESSMENT\n\n"
                "People risk indicators exist, but employee mapping information is incomplete."
            )

        df = pd.DataFrame(rows).head(5)

        # ---- LLM for professional narrative ----
        prompt = f"""
You are a Delivery Head reviewing people attrition risk.

Using the data below, identify employees who may be likely to leave.

Data:
{df.to_dict(orient="records")}

Respond in a professional, leadership tone.

Provide:
- Employee Name
- Employee ID
- Team
- Clear reason for attrition risk
- Leadership recommendation

Do NOT mention models, algorithms, or internal metrics.
"""

        explanation = explain_insight(prompt)
        return explanation or df.to_string(index=False)

    # =========================================================
    # 🔵 TEAM UTILIZATION
    # =========================================================
    if "team" in q and "utilization" in q:
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

        prompt = f"""
You are a Delivery Head reviewing team utilization.

Low utilization teams:
{low_teams.to_dict(orient="records")}

Explain:
- What this indicates
- Why it matters
- What leadership should do next
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 DELIVERY RISK
    # =========================================================
    if any(k in q for k in ["delivery risk", "delivery", "delay", "miss deadlines"]):
        risky = risk_df[risk_df["risk_flag"] == 1].head(5)

        if risky.empty:
            return "No projects currently show strong delivery risk indicators."

        prompt = f"""
You are a Program Director reviewing delivery health.

Projects at risk:
{risky.to_dict(orient="records")}

Explain:
- Why these projects are at risk
- Impact on delivery timelines
- Immediate corrective actions
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 FINANCIAL / MARGIN
    # =========================================================
    if any(k in q for k in ["margin", "loss", "financial", "profit", "cost"]):
        loss = cost_df[cost_df["margin"] < 0].head(5)

        if loss.empty:
            return "All projects are currently operating within acceptable financial margins."

        prompt = f"""
You are a Delivery & Finance leader reviewing project margins.

Loss-making projects:
{loss.to_dict(orient="records")}

Explain:
- Why margins are negative
- Business impact
- What actions should be taken immediately
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 HR / PEOPLE RISK (NON-ATTRITION)
    # =========================================================
    if any(k in q for k in ["hr", "attendance", "performance", "people"]):
        hr_risk = hr_df[hr_df["hr_risk"] == 1].head(5)

        if hr_risk.empty:
            return "No significant HR risk indicators detected at this time."

        prompt = f"""
You are an HR and Delivery leader reviewing people risk.

Employees with HR risk indicators:
{hr_risk.to_dict(orient="records")}

Explain:
- What risks are visible
- Why they matter
- Recommended actions
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 FALLBACK — GENERAL DELIVERY INTELLIGENCE
    # =========================================================
    return explain_insight(
        "Answer the following delivery intelligence question professionally:\n"
        + question
    )
