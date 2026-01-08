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
# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Agentic AI – Project & Delivery Intelligence",
    page_icon="🧠",
    layout="wide"
)

# ===============================
# TOP HEADER (LOGO + TITLE)
# ===============================
header_col1, header_col2 = st.columns([1, 6])

with header_col1:
    st.image(
        "assets/compunnel_logo.png",
        width=160
    )

with header_col2:
    st.markdown(
        """
        <div style="padding-top:10px">
            <h1 style="margin-bottom:0px;">Agentic AI – Project & Delivery Intelligence</h1>
            <p style="color:gray; margin-top:4px;">
                Enterprise-grade utilization, delivery risk, cost & HR intelligence
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")


# ===============================
# FILE UPLOAD
# ===============================
st.sidebar.header("📂 Upload Data")
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

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    if len(lines) < 2:
        raise ValueError("File has no data rows")

    sample = lines[1]
    delimiter = None
    for d in [",", ";", "\t", "|"]:
        if sample.count(d) >= 5:
            delimiter = d
            break
    if delimiter is None:
        raise ValueError("Unable to detect delimiter")

    header = lines[0].split(delimiter)
    if len(header) < len(REQUIRED_COLS):
        st.warning("⚠️ Malformed header detected. Auto-repairing.")
        header_line = delimiter.join(REQUIRED_COLS)
        csv_text = "\n".join([header_line] + lines[1:])
    else:
        csv_text = "\n".join(lines)

    df = pd.read_csv(io.StringIO(csv_text), sep=delimiter, engine="python")
    return df


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

    if not rows:
        raise ValueError("No usable tabular data found in PDF")

    return pd.DataFrame(rows, columns=REQUIRED_COLS)

# ===============================
# STRICT LOADER (NO FALLBACK)
# ===============================
def load_uploaded_data(file):
    if file is None:
        st.warning("Please upload a file to proceed.")
        st.stop()

    file_bytes = file.getvalue()
    ext = file.name.lower().split(".")[-1]

    try:
        if ext == "xlsx":
            df = parse_excel(file_bytes)
        elif ext in ["csv", "txt"]:
            df = parse_csv_txt(file_bytes)
        elif ext == "pdf":
            df = parse_pdf(file_bytes)
        else:
            st.error("Unsupported file format")
            st.stop()
    except Exception as e:
        st.error("❌ Failed to parse uploaded file")
        st.code(str(e))
        st.stop()

    # Normalize column names
    df.columns = (
        df.columns.astype(str)
        .str.strip().str.lower()
        .str.replace(" ", "_")
    )

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error("❌ Required columns missing")
        st.write("Missing columns:", list(missing))
        st.stop()

    # Convert numerics
    numeric_cols = [
        "hours_logged", "cost_per_hour", "billing_rate",
        "attendance_pct", "leave_days", "performance_rating",
        "experience_years", "story_points", "planned_hours"
    ]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    st.success("✅ Uploaded data validated successfully")
    st.write("Detected columns:", list(df.columns))
    return df

# ===============================
# LOAD DATA
# ===============================
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
# ANALYSIS DASHBOARD
# ===============================
st.sidebar.header("⚙️ Controls")
use_llm = st.sidebar.checkbox("Generate Executive AI Summary (LLM)")

if st.button("🚀 Run AI Analysis"):
    with st.spinner("Running multi-agent analysis..."):
        result = orchestrator.analyze(
            util_df, risk_df, cost_df, hr_df, use_llm
        )

    st.subheader("📉 Underutilized Employees")
    st.dataframe(result["low_util"], use_container_width=True)

    st.subheader("🚨 Delivery Risk Projects (Jira)")
    st.dataframe(result["risk_projects"], use_container_width=True)

    st.subheader("💰 Loss-Making / Margin Risk Projects")
    st.dataframe(result["loss_projects"], use_container_width=True)

    st.subheader("⚠️ HR Risk Indicators")
    st.dataframe(result["hr_risks"], use_container_width=True)

    if use_llm and result["explanation"]:
        st.subheader("🧠 Executive AI Summary")
        st.success(result["explanation"])

# ===============================
# 🤖 CONVERSATIONAL AI BOT
# ===============================
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

user_question = st.text_input(
    "Ask about utilization, Jira risk, HR issues, cost overrun, margin, etc."
)

if st.button("🧠 Get Answer"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing..."):
            answer = answer_question(
                user_question,
                util_df,
                risk_df,
                cost_df,
                hr_df
            )
        st.success(answer)


