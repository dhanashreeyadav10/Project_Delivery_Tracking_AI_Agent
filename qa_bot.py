import pandas as pd
from llm_groq import explain_insight


def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower()

    # =========================================================
    # 🔴 PRIORITY 1: ATTRITION / LIKELY TO LEAVE (OVERRIDE)
    # =========================================================
    if any(k in q for k in [
        "likely to leave", "attrition", "people leave",
        "resign", "quit", "leave the company"
    ]):
        risky = hr_df[hr_df["hr_risk"] == 1]

        if risky.empty:
            return "At this time, I do not see any employees showing strong attrition risk signals."

        # enrich with employee name & team
        emp_map = (
            data[["employee_id", "employee_name", "department"]]
            .drop_duplicates()
            .set_index("employee_id")
        )

        rows = []
        for _, r in risky.iterrows():
            emp = emp_map.loc.get(r["employee_id"])
            if emp is not None:
                rows.append({
                    "employee_id": r["employee_id"],
                    "employee_name": emp["employee_name"],
                    "team": emp["department"],
                    "attendance": r["avg_attendance"],
                    "rating": r["avg_rating"]
                })

        df = pd.DataFrame(rows).head(5)

        # build factual context for LLM
        context = df.to_dict(orient="records")

        prompt = f"""
You are a Delivery Head reviewing people risk.

From the following data, identify employees likely to leave.
Explain in a professional, leadership tone.

Data:
{context}

Provide:
- Employee Name
- Employee ID
- Team
- Clear reason for attrition risk
- Leadership recommendation

Do NOT mention data sources or models.
Keep it executive-ready.
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 TEAM UTILIZATION (ONLY IF TEAM QUESTION)
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
            team_util["total_hours"] / (team_util["employee_count"] * 160)
        ) * 100

        low_teams = team_util.sort_values("utilization_pct").head(3)

        prompt = f"""
You are a Delivery Head.

These teams have low utilization:
{low_teams.to_dict(orient="records")}

Explain:
- What this means
- Why it matters
- What leadership should do next
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 DELIVERY RISK
    # =========================================================
    if "delivery" in q or "risk" in q:
        risky = risk_df[risk_df["risk_flag"] == 1].head(5)

        prompt = f"""
You are a Program Director reviewing delivery health.

Risky projects:
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
    if any(k in q for k in ["margin", "loss", "financial", "profit"]):
        loss = cost_df[cost_df["margin"] < 0].head(5)

        prompt = f"""
You are a Finance + Delivery leader.

Loss-making projects:
{loss.to_dict(orient="records")}

Explain:
- Why margins are negative
- Business risk
- What should be done immediately
"""

        return explain_insight(prompt)

    # =========================================================
    # 🔵 FALLBACK
    # =========================================================
    return explain_insight(
        "Answer the following delivery intelligence question professionally:\n" + question
    )
