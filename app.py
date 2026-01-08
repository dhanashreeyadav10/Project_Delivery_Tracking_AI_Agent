import streamlit as st
import pandas as pd
import io
import re

# ===============================
# INTERNAL IMPORTS
# ===============================
from models import (
    utilization_model,
    delivery_risk_model,
    cost_margin_model,
    hr_health_model
)
from orchestrator import Orchestrator
from qa_bot import answer_question

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Agentic AI – Delivery Intelligence",
    layout="wide"
)

# ===============================
# SIDEBAR – BRANDING
# ===============================
st.sidebar.image("compunnel_logo.jpg", use_column_width=True)
st.sidebar.markdown("---")

# ===============================
# TITLE
# ===============================
st.title("🤖 Ask Delivery Intelligence Bot")
st.caption("Ask about teams, utilization, delivery risk, HR or margin")

# ===============================
# FILE UPLOAD
# ===============================
st.sidebar.header("📂 Upload Delivery Data (CSV / Excel)")
uploaded_file = st.sidebar.file_uploader(
    "Upload Delivery Data",
    type=["csv", "xlsx"]
)

REQUIRED_COLS = [
    "employee_id", "employee_name", "department", "designation",
    "employment_type", "location", "experience_years", "cost_per_hour",
    "manager_id", "project_id", "project_name", "client_name",
    "project_type", "start_date", "end_date", "planned_hours",
    "billing_rate", "work_date", "hours_logged", "billable",
    "task_type", "jira_ticket", "ticket_status", "priority",
    "story_points", "attendance_pct", "leave_days", "performance_rating"
]

# ===============================
# FILE LOADER
# ===============================
def load_data(file):
    if file is None:
        st.info("Please upload delivery data to proceed.")
        st.stop()

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = (
        df.columns.astype(str)
        .str.strip().str.lower()
        .str.replace(" ", "_")
    )

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error("❌ Missing required columns:")
        st.write(list(missing))
        st.stop()

    # Convert numerics
    numeric_cols = [
        "hours_logged", "cost_per_hour", "billing_rate",
        "attendance_pct", "leave_days", "performance_rating",
        "experience_years", "story_points", "planned_hours"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

# ===============================
# LOAD DATA
# ===============================
data = load_data(uploaded_file)

# ===============================
# RUN MODELS
# ===============================
util_df = utilization_model(data)
risk_df = delivery_risk_model(data)
cost_df = cost_margin_model(data)
hr_df = hr_health_model(data)

# ===============================
# CHAT INPUT
# ===============================
st.markdown("---")
user_question = st.text_input(
    "💬 Ask a question",
    placeholder="e.g. Are there people likely to leave? If yes, list their name, employee id and team name"
)

if st.button("🧠 Get Answer"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing..."):
            answer = answer_question(
                user_question,
                data,
                util_df,
                risk_df,
                cost_df,
                hr_df
            )

        # ===============================
        # ✅ CORRECT RENDERING LOGIC
        # ===============================
        if isinstance(answer, pd.DataFrame):
            st.subheader("📋 Result")
            st.dataframe(answer, use_container_width=True)
        else:
            st.success(answer)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("© 2026 Compunnel Digital | Agentic AI – Delivery Intelligence Platform")
