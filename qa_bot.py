import pandas as pd
from llm_groq import explain_insight


def answer_question(question, data, util_df, risk_df, cost_df, hr_df):
    q = question.lower().strip()

    # =========================================================
    # ATTRITION / LIKELY TO LEAVE (TABULAR BY DEFAULT)
    # =========================================================
    if any(k in q for k in [
        "likely to leave", "attrition",
        "resign", "quit", "leave the company"
    ]):
        risky = hr_df[hr_df["hr_risk"] == 1]

        if risky.empty:
            return "No employees currently show strong attrition risk signals."

        # Safe lookup
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
                "Employee ID": emp_id,
                "Employee Name": emp["employee_name"],
                "Team": emp["department"],
                "Avg Attendance (%)": round(r["avg_attendance"], 1),
                "Performance Rating": round(r["avg_rating"], 1)
            })

        df = pd.DataFrame(rows)

        # 👉 ALWAYS RETURN DATAFRAME FOR ATTRITION QUESTIONS
        return df.head(10)

    # =========================================================
    # TEAM UTILIZATION
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

        team_util["Utilization %"] = (
            team_util["total_hours"] /
            (team_util["employee_count"] * 160)
        ) * 100

        team_util["Utilization %"] = team_util["Utilization %"].clip(upper=100)
        return team_util.sort_values("Utilization %").head(5)

    # =========================================================
    # DELIVERY RISK
    # =========================================================
    if "delivery" in q or "risk" in q:
        risky = risk_df[risk_df["risk_flag"] == 1].head(5)

        if risky.empty:
            return "No projects currently show delivery risk."

        return explain_insight(
            f"You are a Delivery Head. Explain the risks:\n{risky.to_dict(orient='records')}"
        )

    # =========================================================
    # FINANCIAL / MARGIN
    # =========================================================
    if any(k in q for k in ["margin", "loss", "financial", "profit"]):
        loss = cost_df[cost_df["margin"] < 0].head(5)

        if loss.empty:
            return "All projects are financially healthy."

        return explain_insight(
            f"You are a Finance leader. Explain the margin risks:\n{loss.to_dict(orient='records')}"
        )

    # =========================================================
    # FALLBACK
    # =========================================================
    return explain_insight(question)
