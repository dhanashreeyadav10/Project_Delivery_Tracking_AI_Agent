import streamlit as st
import pandas as pd
import io
import re
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

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
    page_title="Agentic AI – Project & Delivery Intelligence",
    page_icon="🧠",
    layout="wide"
)

# ===============================
# PROFESSIONAL HEADER
# ===============================
st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        align-items: center;
        gap: 20px;
        padding: 10px 0 20px 0;
    }
    .header-title {
        font-size: 38px;
        font-weight: 700;
    }
    .header-subtitle {
        color: #6b7280;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

col1, col2 = st.columns([1, 7])

with col1:
    st.image("compunnel_logo.jpg", width=140)

with col2:
    st.markdown(
        """
        <div class="header-container">
            <div>
                <div class="header-title">
                    Agentic AI – Project & Delivery Intelligence
                </div>
                <div class="header-subtitle">
                    Enterprise-grade utilization, delivery risk, cost & HR intelligence
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ===============================
# SIDEBAR
# ===============================
st.sidebar.image("compunnel_logo.jpg", width=180)
st.sidebar.markdown("---")

st.sidebar.header("📂 Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "Upload Delivery Data (Excel / CSV / TXT / PDF)",
    type=["xlsx", "csv", "txt", "pdf"]
)

st.sidebar.header("🧑‍💼 Role View")
role = st.sidebar.radio(
    "Select Role",
    ["Delivery Head", "HR", "Finance"]
)

use_llm = st.sidebar.checkbox("Generate Executive AI Summary")

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
    df = pd.read_csv(io.StringIO(text))
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
    return pd.DataFrame(rows, columns=REQUIRED_COLS)

# ===============================
# LOAD DATA
# ===============================
def load_uploaded_data(file):
    if not file:
        st.warning("Please upload a file to proceed.")
        st.stop()

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
        st.stop()

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error(f"Missing required columns: {list(missing)}")
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
# MODELS
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
# PDF REPORT
# ===============================
def generate_pdf_report(kpis, summary):
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(temp.name, pagesize=A4)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("<b>Executive Delivery Intelligence Report</b>", styles["Title"]),
        Paragraph(f"Utilization Health: {kpis['util']}%", styles["Normal"]),
        Paragraph(f"Delivery Risk Health: {kpis['risk']}%", styles["Normal"]),
        Paragraph(f"Margin Health: {kpis['margin']}%", styles["Normal"]),
        Paragraph("<br/><b>AI Summary</b>", styles["Heading2"]),
        Paragraph(summary or "N/A", styles["Normal"]),
    ]

    doc.build(content)
    return temp.name

# ===============================
# RUN ANALYSIS
# ===============================
if st.button("🚀 Run AI Analysis"):
    result = orchestrator.analyze(
        util_df, risk_df, cost_df, hr_df, use_llm
    )

    # KPI CALCULATION
    util_kpi = round((1 - len(result["low_util"]) / util_df.shape[0]) * 100, 1)
    risk_kpi = round((1 - len(result["risk_projects"]) / risk_df.shape[0]) * 100, 1)
    margin_kpi = round((1 - len(result["loss_projects"]) / cost_df.shape[0]) * 100, 1)

    st.markdown("### 📊 Executive KPIs")
    c1, c2, c3 = st.columns(3)
    c1.metric("Utilization Health %", f"{util_kpi}%")
    c2.metric("Delivery Risk Health %", f"{risk_kpi}%")
    c3.metric("Margin Health %", f"{margin_kpi}%")

    st.divider()

    # ROLE-BASED VIEWS
    if role == "Delivery Head":
        st.subheader("🚨 Delivery Risk Projects")
        st.dataframe(result["risk_projects"], use_container_width=True)

        st.subheader("📉 Underutilized Employees")
        st.dataframe(result["low_util"], use_container_width=True)

    elif role == "HR":
        st.subheader("⚠️ HR Risk Indicators")
        st.dataframe(result["hr_risks"], use_container_width=True)

    elif role == "Finance":
        st.subheader("💰 Loss / Margin Risk Projects")
        st.dataframe(result["loss_projects"], use_container_width=True)

    # EXECUTIVE SUMMARY + PDF
    if use_llm and result["explanation"]:
        st.subheader("🧠 Executive AI Summary")
        st.success(result["explanation"])

        pdf = generate_pdf_report(
            {"util": util_kpi, "risk": risk_kpi, "margin": margin_kpi},
            result["explanation"]
        )

        with open(pdf, "rb") as f:
            st.download_button(
                "📄 Download Executive PDF Report",
                f,
                file_name="Delivery_Intelligence_Report.pdf",
                mime="application/pdf"
            )

# ===============================
#Chat Bot
# ===============================
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask about utilization, delivery risk, HR or margin"
)

if st.button("🧠 Get Answer"):
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Analyzing..."):
            answer = answer_question(
                question, util_df, risk_df, cost_df, hr_df
            )
        st.success(answer)


# ===============================
# FOOTER
# ===============================
st.markdown(
    """
    <hr>
    <div style="text-align:center; color:gray; font-size:13px;">
        © 2026 Compunnel Digital | Agentic AI – Delivery Intelligence Platform
    </div>
    """,
    unsafe_allow_html=True
)



