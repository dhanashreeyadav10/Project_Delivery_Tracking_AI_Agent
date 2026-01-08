import pandas as pd

def utilization_model(df):
    util = df.groupby("employee_id")["hours_logged"].sum().reset_index()
    util["utilization_pct"] = (util["hours_logged"] / 160) * 100
    return util


def delivery_risk_model(df):
    risk = (
        df.groupby("project_id")
        .agg(
            open_tickets=("ticket_status", lambda x: (x != "Done").sum()),
            high_priority=("priority", lambda x: x.isin(["High", "Critical"]).sum())
        )
        .reset_index()
    )
    risk["risk_flag"] = ((risk["open_tickets"] > 5) | (risk["high_priority"] > 3)).astype(int)
    return risk


def cost_margin_model(df):
    df = df.copy()
    df["delivery_cost"] = df["hours_logged"] * df["cost_per_hour"]
    df["revenue"] = df["hours_logged"] * df["billing_rate"] * df["billable"]

    summary = (
        df.groupby("project_id")
        .agg(
            total_cost=("delivery_cost", "sum"),
            total_revenue=("revenue", "sum"),
            planned_hours=("planned_hours", "max"),
            avg_cost=("cost_per_hour", "mean")
        )
        .reset_index()
    )

    summary["planned_cost"] = summary["planned_hours"] * summary["avg_cost"]
    summary["margin"] = summary["total_revenue"] - summary["total_cost"]
    return summary


def hr_health_model(df):
    hr = (
        df.groupby("employee_id")
        .agg(
            avg_attendance=("attendance_pct", "mean"),
            avg_rating=("performance_rating", "mean")
        )
        .reset_index()
    )
    hr["hr_risk"] = ((hr["avg_attendance"] < 90) | (hr["avg_rating"] < 3.5)).astype(int)
    return hr
