import streamlit as st
import pandas as pd
import io
import re
from PIL import Image

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
    page_title="Agentic AI – Delivery Intelligence | Compunnel",
    layout="wide"
)

# ===============================
# HEADER WITH LOGO
# ===============================
logo = Image.open("compunnel_logo.jpg")

col1, col2 = st.columns([1, 6])

with col1:
    st.image(logo, width=120)

with col2:
    st.markdown(
        """
        <h1 style="margin-bottom:0;">Agentic AI – Project & Delivery Intelligence</h1>
        <p style="color:gray; margin-top:0;">
        Enterprise Delivery, Cost, HR & Risk Intelligence Platform
        </p>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# ===============================
# GLOBAL STYLING
# ===============================
st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; }
    h1 { font-weight: 700; }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# SIDEBAR
# ===============================
st.sidebar.header("📂 Upload Delivery Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload Excel / CSV / TXT / PDF",
    type=["xlsx", "csv", "txt", "pdf"]
)

st.sidebar.markdown(
    """
    <hr>
    <div style="font-size:13px;color:gray;">
    <b>Powered by Compunnel</b><br>
    Agentic AI Delivery Intelligence
    </div>
    """,
    unsafe_allow_html=True
)

# ===============================
# REQUIRED COLUMNS
# ===============================
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

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    delimiter = "," if "," in lines[0] else "|"
    return pd.read_csv(io.StringIO("\n".join(lines)), sep=delimiter)


def parse_pdf(file_bytes):
    import pdfplumber
    rows = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                parts = re.split(r"[,\s]+", line)
                if len(parts) >= len(REQUIRED_COLS):
                    rows.append(parts[:len(REQUIRED_COLS)])
    return pd.DataFrame(rows, columns=REQUIRED_COLS)

# ===============================
# LOAD DATA
# ===============================
def load_uploaded_data(file):
    if file is None:
        st.info("Please upload a delivery dataset to begin.")
        st.stop()

    ext = file.name.split(".")[-1].lower()
    file_bytes = file.getvalue()

    if ext == "xlsx":
        df = parse_excel(file_bytes)
    elif ext in ["csv", "txt"]:
        df = parse_csv_txt(file_bytes)
    elif ext == "pdf":
        df = parse_pdf(file_bytes)
    else:
        st.error("Unsupported format")
        st.stop()

    df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error(f"Missing required columns: {missing}")
        st.stop()

    numeric_cols = [
        "hours_logged", "cost_per_hour", "billing_rate",
        "attendance_pct", "leave_days", "performance_rating",
        "experience_years", "story_points", "planned_hours"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    st.success("✅ Data validated successfully")
    return df


data = load_uploaded_data(uploaded_file)

# ===============================
# RUN MODELS
# ===============================
util_df = utilization_model(data)
risk_df = delivery_risk_model(data)
cost_df = cost_margin_model(data)
hr_df = hr_health_model(data)

# ===============================
# ORCHESTRATOR
# ===============================
@st.cache_resource
def load_orchestrator():
    return Orchestrator()

orchestrator = load_orchestrator()

# ===============================
# CONTROLS
# ===============================
st.sidebar.header("⚙️ Controls")
use_llm = st.sidebar.checkbox("Generate Executive AI Summary")

if st.button("🚀 Run AI Analysis"):
    result = orchestrator.analyze(
        util_df, risk_df, cost_df, hr_df, use_llm
    )

    st.subheader("📉 Underutilized Employees")
    st.dataframe(result["low_util"], use_container_width=True)

    st.subheader("🚨 Delivery Risk Projects")
    st.dataframe(result["risk_projects"], use_container_width=True)

    st.subheader("💰 Loss / Margin Risk Projects")
    st.dataframe(result["loss_projects"], use_container_width=True)

    st.subheader("⚠️ HR Risk Indicators")
    st.dataframe(result["hr_risks"], use_container_width=True)

    if use_llm:
        st.subheader("🧠 Executive AI Summary")
        st.success(result["explanation"])

# ===============================
# QA BOT
# ===============================
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask about utilization, cost, risk, HR, margin, attrition, etc."
)

if st.button("🧠 Get Answer"):
    answer = answer_question(
        question, util_df, risk_df, cost_df, hr_df
    )
    st.success(answer)

