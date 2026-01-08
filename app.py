import streamlit as st

# 🚨 MUST BE FIRST
st.set_page_config(
    page_title="Agentic AI – Delivery Intelligence | Compunnel",
    layout="wide"
)

import pandas as pd
from PIL import Image

from models import *
from orchestrator import Orchestrator
from qa_bot import answer_question

# ---------------- HEADER ----------------
logo = Image.open("compunnel_logo.jpg")
c1, c2 = st.columns([1, 6])

with c1:
    st.image(logo, width=120)

with c2:
    st.markdown("""
    <h1>Agentic AI – Project & Delivery Intelligence</h1>
    <p style="color:gray;">
    Enterprise Delivery, Cost, HR & Risk Intelligence Platform
    </p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Upload Delivery Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload CSV or Excel",
    type=["csv", "xlsx"]
)

# ---------------- LOAD DATA ----------------
def load_data(file):
    if not file:
        st.info("Upload a dataset to begin.")
        st.stop()

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    numeric = [
        "hours_logged","cost_per_hour","billing_rate",
        "attendance_pct","leave_days","performance_rating",
        "experience_years","story_points","planned_hours"
    ]
    for c in numeric:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

data = load_data(uploaded_file)

# ---------------- RUN MODELS ----------------
util_df = utilization_model(data)
risk_df = delivery_risk_model(data)
cost_df = cost_margin_model(data)
hr_df   = hr_health_model(data)

orchestrator = Orchestrator()

if st.button("🚀 Run AI Analysis"):
    result = orchestrator.analyze(util_df, risk_df, cost_df, hr_df)

    st.subheader("📉 Underutilized Employees")
    st.dataframe(result["low_util"])

    st.subheader("🚨 Delivery Risk Projects")
    st.dataframe(result["risk_projects"])

    st.subheader("💰 Loss-Making Projects")
    st.dataframe(result["loss_projects"])

    st.subheader("⚠️ HR Risk Employees")
    st.dataframe(result["hr_risks"])

    st.subheader("🧠 Executive Summary")
    st.success(result["summary"])

# ---------------- CHAT BOT ----------------
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input("Ask a business question")

if st.button("🧠 Get Answer"):
    answer = answer_question(
        question, util_df, risk_df, cost_df, hr_df
    )
    st.success(answer)
