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

st.set_page_config(
    page_title="🧠 Agentic AI – Project & Delivery Tracking",
    layout="wide"
)

st.title("🧠 Agentic AI – Project & Delivery Intelligence")

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
# FILE PARSERS (UNCHANGED)
# ===============================
def parse_excel(file_bytes):
    return pd.read_excel(io.BytesIO(file_bytes))

def parse_csv_txt(file_bytes):
    import chardet
    encoding = chardet.detect(file_bytes).get("encoding", "utf-8")
    text = file_bytes.decode(encoding, errors="ignore")

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    sample = lines[1]
    for d in [",", ";", "\t", "|"]:
        if sample.count(d) >= 5:
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
# SAFE LOADER (NO st.stop)
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
        st.error("Failed to parse file")
        st.code(str(e))
        return None

# ===============================
# LOAD DATA
# ===============================
data = load_uploaded_data(uploaded_file)

if data is not None:
    util_df = utilization_model(data)
    risk_df = delivery_risk_model(data)
    cost_df = cost_margin_model(data)
    hr_df = hr_health_model(data)

# ===============================
# CHATBOT
# ===============================
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask about utilization, delivery risk, HR, margin, etc.",
    disabled=data is None
)

if st.button("🧠 Get Answer", disabled=data is None):
    result = answer_question(
        question,
        util_df,
        risk_df,
        cost_df,
        hr_df
    )

    if isinstance(result, pd.DataFrame):
        st.dataframe(result, use_container_width=True)
    else:
        st.success(result)
