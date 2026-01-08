import streamlit as st

# =========================================================
# 🚨 THIS MUST BE THE FIRST STREAMLIT COMMAND — NO EXCEPTIONS
# =========================================================
st.set_page_config(
    page_title="Agentic AI – Delivery Intelligence | Compunnel",
    layout="wide"
)
import os
st.sidebar.write("GROQ KEY LOADED:", bool(os.getenv("GROQ_API_KEY")))


# =========================================================
# IMPORTS (SAFE AFTER PAGE CONFIG)
# =========================================================
import pandas as pd
from PIL import Image

from models import (
    utilization_model,
    delivery_risk_model,
    cost_margin_model,
    hr_health_model
)
from orchestrator import Orchestrator
from qa_bot import answer_question

# =========================================================
# HEADER WITH LOGO
# =========================================================
logo = Image.open("compunnel_logo.jpg")

col1, col2 = st.columns([1, 6])
with col1:
    st.image(logo, width=120)

with col2:
    st.markdown("""
    <h1 style="margin-bottom:0;">Agentic AI – Project & Delivery Intelligence</h1>
    <p style="color:gray;">Enterprise Delivery, Cost, HR & Risk Intelligence Platform</p>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# SIDEBAR
# =========================================================
st.sidebar.header("📂 Upload Delivery Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel / CSV",
    type=["xlsx", "csv"]
)

st.sidebar.markdown("""
<hr>
<b>Powered by Compunnel</b><br>
Agentic AI Delivery Intelligence
""", unsafe_allow_html=True)

# =========================================================
# REQUIRED COLUMNS
# =========================================================
REQUIRED_COLS = [
    "employee_id","employee_name","department","designation","employment_type",
    "location","experience_years","cost_per_hour","manager_id","project_id",
    "project_name","client_name","project_type","start_date","end_date",
    "planned_hours","billing_rate","work_date","hours_logged","billable",
    "task_type","jira_ticket","ticket_status","priority","story_points",
    "attendance_pct","leave_days","performance_rating"
]

# =========================================================
# LOAD DATA
# =========================================================
def load_data(file):
    if not file:
        st.info("Please upload a delivery dataset to begin.")
        st.stop()

    if file.name.endswith(".xlsx"):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()

    numeric_cols = [
        "hours_logged","cost_per_hour","billing_rate","attendance_pct",
        "leave_days","performance_rating","experience_years",
        "story_points","planned_hours"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    st.success("✅ Data validated successfully")
    return df

data = load_data(uploaded_file)

# =========================================================
# RUN MODELS
# =========================================================
util_df = utilization_model(data)
risk_df = delivery_risk_model(data)
cost_df = cost_margin_model(data)
hr_df = hr_health_model(data)

# =========================================================
# ORCHESTRATOR
# =========================================================
orchestrator = Orchestrator()
use_llm = st.sidebar.checkbox("Generate Executive AI Summary", value=True)

if st.button("🚀 Run AI Analysis"):
    result = orchestrator.analyze(
        util_df, risk_df, cost_df, hr_df, use_llm
    )

    st.subheader("📉 Underutilized Employees")
    st.dataframe(result["low_util"], use_container_width=True)

    st.subheader("🚨 Delivery Risk Projects")
    st.dataframe(result["risk_projects"], use_container_width=True)

    st.subheader("💰 Loss-Making Projects")
    st.dataframe(result["loss_projects"], use_container_width=True)

    st.subheader("⚠️ HR Risk Employees")
    st.dataframe(result["hr_risks"], use_container_width=True)

    if use_llm:
        st.subheader("🧠 Executive AI Summary")
        st.success(result["explanation"])

# =========================================================
# QA BOT
# =========================================================
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask about utilization, cost, risk, HR, margin, attrition, etc.",
    placeholder="Are there people likely to leave?"
)

if st.button("🧠 Get Answer"):
    with st.spinner("Analyzing with LLM..."):
        answer = answer_question(
            question, util_df, risk_df, cost_df, hr_df
        )
    st.success(answer)

