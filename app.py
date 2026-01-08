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

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Agentic AI – Project & Delivery Intelligence",
    layout="wide"
)

# ---------------- SIDEBAR ----------------
st.sidebar.image("compunnel_logo.jpg", use_container_width=True)
st.sidebar.header("📂 Upload Delivery Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload Delivery Data (CSV / Excel / TXT / PDF)",
    type=["csv", "xlsx", "txt", "pdf"]
)

# ---------------- REQUIRED COLUMNS ----------------
REQUIRED_COLS = [
    "employee_id", "employee_name", "department", "designation",
    "employment_type", "location", "experience_years", "cost_per_hour",
    "manager_id", "project_id", "project_name", "client_name",
    "project_type", "start_date", "end_date", "planned_hours",
    "billing_rate", "work_date", "hours_logged", "billable",
    "task_type", "jira_ticket", "ticket_status", "priority",
    "story_points", "attendance_pct", "leave_days", "performance_rating"
]

# ---------------- FILE PARSERS ----------------
def parse_excel(b):
    return pd.read_excel(io.BytesIO(b))

def parse_csv_txt(b):
    return pd.read_csv(io.StringIO(b.decode("utf-8", errors="ignore")))

def parse_pdf(b):
    import pdfplumber
    rows = []
    with pdfplumber.open(io.BytesIO(b)) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            for line in text.split("\n"):
                parts = re.split(r"[,\s]+", line)
                if len(parts) >= len(REQUIRED_COLS):
                    rows.append(parts[:len(REQUIRED_COLS)])
    return pd.DataFrame(rows, columns=REQUIRED_COLS)

# ---------------- LOAD DATA ----------------
def load_data(file):
    if file is None:
        st.info("⬅️ Upload a dataset to begin")
        st.stop()

    ext = file.name.split(".")[-1].lower()
    data = file.getvalue()

    try:
        if ext == "xlsx":
            df = parse_excel(data)
        elif ext in ["csv", "txt"]:
            df = parse_csv_txt(data)
        elif ext == "pdf":
            df = parse_pdf(data)
        else:
            st.error("Unsupported file format")
            st.stop()
    except Exception as e:
        st.error(f"File parsing failed: {e}")
        st.stop()

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error(f"Missing columns: {missing}")
        st.stop()

    numeric_cols = [
        "hours_logged", "cost_per_hour", "billing_rate",
        "attendance_pct", "leave_days", "performance_rating",
        "experience_years", "planned_hours"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df

data = load_data(uploaded_file)

# ---------------- MODELS ----------------
util_df = utilization_model(data)
risk_df = delivery_risk_model(data)
cost_df = cost_margin_model(data)
hr_df = hr_health_model(data)

# ---------------- ORCHESTRATOR ----------------
@st.cache_resource
def load_orchestrator():
    return Orchestrator()

orchestrator = load_orchestrator()

# ---------------- UI ----------------
st.title("🧠 Agentic AI – Project & Delivery Intelligence")

st.sidebar.header("⚙️ Controls")
use_llm = st.sidebar.checkbox("Generate Executive AI Summary (LLM)")

# ---------------- ANALYSIS SECTION ----------------
if st.button("🚀 Run AI Analysis"):
    result = orchestrator.analyze(
        util_df, risk_df, cost_df, hr_df, use_llm
    )

    st.subheader("📉 Underutilized Employees")
    st.dataframe(result["low_util"], use_container_width=True)

    st.subheader("🚨 Delivery Risk Projects")
    st.dataframe(result["risk_projects"], use_container_width=True)

    st.subheader("💰 Margin Risk Projects")
    st.dataframe(result["loss_projects"], use_container_width=True)

    st.subheader("⚠️ HR Risk Employees")
    st.dataframe(result["hr_risks"], use_container_width=True)

    st.subheader("🧠 Executive AI Summary")
    st.success(result["explanation"])

# ---------------- CHAT BOT ----------------
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask a question",
    placeholder="Are there people likely to leave? If yes, list their name, employee id and team name"
)

if st.button("🧠 Get Answer"):
    answer = answer_question(
        question, util_df, risk_df, cost_df, hr_df
    )

    if isinstance(answer, pd.DataFrame):
        st.dataframe(answer, use_container_width=True)
    else:
        st.info(answer)

st.markdown(
    "<hr/><center>© 2026 Compunnel Digital | Agentic AI – Delivery Intelligence Platform</center>",
    unsafe_allow_html=True
)
