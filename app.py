import streamlit as st
import pandas as pd
import io
import re

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
    page_title="🧠 Agentic AI – Project & Delivery Tracking",
    layout="wide"
)

st.title("🧠 Agentic AI – Project & Delivery Intelligence")

# ===============================
# FILE UPLOAD (LEFT PANEL)
# ===============================
st.sidebar.header("📂 Upload Delivery Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload Delivery Data (Excel / CSV / TXT / PDF)",
    type=["xlsx", "csv", "txt", "pdf"]
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
# FILE PARSERS
# ===============================
def parse_excel(file_bytes):
    return pd.read_excel(io.BytesIO(file_bytes))

def parse_csv_txt(file_bytes):
    import chardet
    encoding = chardet.detect(file_bytes).get("encoding", "utf-8")
    text = file_bytes.decode(encoding, errors="ignore")

    for d in [",", ";", "\t", "|"]:
        if text.count(d) > 10:
            return pd.read_csv(io.StringIO(text), sep=d)

    raise ValueError("Unable to detect delimiter")

def parse_pdf(file_bytes):
    import pdfplumber
    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                parts = re.split(r"[,\s]+", line.strip())
                if len(parts) >= len(REQUIRED_COLS):
                    rows.append(parts[:len(REQUIRED_COLS)])

    return pd.DataFrame(rows, columns=REQUIRED_COLS)

# ===============================
# SAFE DATA LOADER (NO st.stop)
# ===============================
def load_uploaded_data(file):
    if file is None:
        return None

    try:
        ext = file.name.lower().split(".")[-1]
        file_bytes = file.getvalue()

        if ext == "xlsx":
            df = parse_excel(file_bytes)
        elif ext in ["csv", "txt"]:
            df = parse_csv_txt(file_bytes)
        elif ext == "pdf":
            df = parse_pdf(file_bytes)
        else:
            st.error("Unsupported file format")
            return None

        df.columns = (
            df.columns.astype(str)
            .str.strip().str.lower()
            .str.replace(" ", "_")
        )

        missing = set(REQUIRED_COLS) - set(df.columns)
        if missing:
            st.error(f"Missing required columns: {list(missing)}")
            return None

        return df

    except Exception as e:
        st.error("❌ Failed to parse uploaded file")
        st.code(str(e))
        return None

# ===============================
# LOAD DATA
# ===============================
data = load_uploaded_data(uploaded_file)

if data is None:
    st.info("⬅️ Upload delivery data to enable analysis and chatbot.")
    st.stop()

# ===============================
# RUN MODELS (ONCE)
# ===============================
util_df = utilization_model(data)
risk_df = delivery_risk_model(data)
cost_df = cost_margin_model(data)
hr_df = hr_health_model(data)

# ===============================
# ORCHESTRATOR (ANALYSIS MODE)
# ===============================
@st.cache_resource
def load_orchestrator():
    return Orchestrator()

orchestrator = load_orchestrator()

# =========================================================
# 🔹 PART 1: GENERATE ANALYSIS (AGENT-DRIVEN)
# =========================================================
st.sidebar.header("⚙️ Controls")
use_llm = st.sidebar.checkbox("Generate Executive AI Summary (LLM)")

st.markdown("## 🚀 Generate Delivery Analysis")

if st.button("Run AI Analysis"):
    with st.spinner("Running multi-agent analysis..."):
        result = orchestrator.analyze(
            util_df, risk_df, cost_df, hr_df, use_llm
        )

    st.subheader("📉 Underutilized Employees")
    st.dataframe(result["low_util"], use_container_width=True)

    st.subheader("🚨 Delivery Risk Projects")
    st.dataframe(result["risk_projects"], use_container_width=True)

    st.subheader("💰 Loss-Making Projects")
    st.dataframe(result["loss_projects"], use_container_width=True)

    st.subheader("⚠️ HR Risk Indicators")
    st.dataframe(result["hr_risks"], use_container_width=True)

    if result["explanation"]:
        st.subheader("🧠 Executive Summary")
        st.info(result["explanation"])

# =========================================================
# 🔹 PART 2: CONVERSATIONAL AI BOT
# =========================================================
st.markdown("---")
st.markdown("## 🤖 Ask Delivery Intelligence Bot")

user_question = st.text_input(
    "Ask about utilization, delivery risk, HR issues, margin, etc."
)

if st.button("Get Answer"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing your question..."):
            response = answer_question(
                user_question,
                util_df,
                risk_df,
                cost_df,
                hr_df
            )

        # ✅ Proper rendering
        if isinstance(response, pd.DataFrame):
            st.dataframe(response, use_container_width=True)
        else:
            st.success(response)

