import streamlit as st
import pandas as pd
import tempfile

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

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
# SIDEBAR (ONLY LOGO LOCATION)
# ===============================
st.sidebar.image("compunnel_logo.jpg", width=180)
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader(
    "📂 Upload Delivery Data (CSV / Excel)",
    type=["csv", "xlsx"]
)

role = st.sidebar.radio(
    "🧑‍💼 Role View",
    ["Delivery Head", "HR", "Finance"]
)

use_llm = st.sidebar.checkbox("Generate Executive AI Summary")

# ===============================
# MAIN TITLE (NO LOGO HERE)
# ===============================
st.title("🧠 Agentic AI – Project & Delivery Intelligence")
st.caption("Enterprise-grade utilization, delivery risk, cost & HR intelligence")

st.divider()

# ===============================
# REQUIRED COLUMNS
# ===============================
REQUIRED_COLS = [
    "employee_id","employee_name","department","designation",
    "employment_type","location","experience_years","cost_per_hour",
    "manager_id","project_id","project_name","client_name",
    "project_type","start_date","end_date","planned_hours",
    "billing_rate","work_date","hours_logged","billable",
    "task_type","jira_ticket","ticket_status","priority",
    "story_points","attendance_pct","leave_days","performance_rating"
]

# ===============================
# LOAD DATA
# ===============================
def load_data(file):
    if not file:
        st.warning("Please upload a data file to proceed.")
        st.stop()

    df = pd.read_csv(file) if file.name.endswith(".csv") else pd.read_excel(file)
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    missing = set(REQUIRED_COLS) - set(df.columns)
    if missing:
        st.error(f"Missing required columns: {list(missing)}")
        st.stop()

    return df

data = load_data(uploaded_file)

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
# SAFE PDF GENERATOR
# ===============================
def generate_pdf(summary_text: str, kpis: dict):
    if not summary_text:
        summary_text = "No executive summary available."

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    doc = SimpleDocTemplate(tmp.name, pagesize=A4)
    styles = getSampleStyleSheet()

    content = [
        Paragraph("<b>Executive Delivery Intelligence Report</b>", styles["Title"]),
        Paragraph(f"Utilization Health: {kpis['util']}%", styles["Normal"]),
        Paragraph(f"Delivery Risk Health: {kpis['risk']}%", styles["Normal"]),
        Paragraph(f"Margin Health: {kpis['margin']}%", styles["Normal"]),
        Paragraph("<br/><b>Executive Summary</b>", styles["Heading2"]),
        Paragraph(summary_text, styles["Normal"]),
    ]

    doc.build(content)
    return tmp.name

# ===============================
# RUN ANALYSIS
# ===============================
if st.button("🚀 Run AI Analysis"):
    result = orchestrator.analyze(
        util_df, risk_df, cost_df, hr_df, use_llm
    )

    # -----------------------------
    # GUARANTEE EXEC SUMMARY STRING
    # -----------------------------
    explanation = result.get("explanation")
    if not explanation or not isinstance(explanation, str):
        explanation = (
            f"Key Insights:\n"
            f"• Underutilized Employees: {len(result['low_util'])}\n"
            f"• Delivery Risk Projects: {len(result['risk_projects'])}\n"
            f"• Loss-Making Projects: {len(result['loss_projects'])}\n"
            f"• HR Risk Employees: {len(result['hr_risks'])}\n\n"
            "Recommended Actions:\n"
            "• Optimize bench utilization\n"
            "• Prioritize high-risk Jira tickets\n"
            "• Review project cost overruns\n"
            "• Engage HR for early risk mitigation"
        )

    # -----------------------------
    # KPI CALCULATIONS (CORRECT)
    # -----------------------------
    total_employees = util_df["employee_id"].nunique()
    underutilized = util_df[util_df["utilization_pct"] < 60]["employee_id"].nunique()

    total_projects = risk_df["project_id"].nunique()
    risky_projects = risk_df[risk_df["risk_flag"] == 1]["project_id"].nunique()

    loss_projects = cost_df[cost_df["margin"] < 0]["project_id"].nunique()

    util_kpi = round(((total_employees - underutilized) / total_employees) * 100, 1)
    risk_kpi = round(((total_projects - risky_projects) / total_projects) * 100, 1)
    margin_kpi = round(((total_projects - loss_projects) / total_projects) * 100, 1)

    # -----------------------------
    # KPI DISPLAY
    # -----------------------------
    st.subheader("📊 Executive KPIs")
    c1, c2, c3 = st.columns(3)
    c1.metric("Utilization Health %", f"{util_kpi}%")
    c2.metric("Delivery Risk Health %", f"{risk_kpi}%")
    c3.metric("Margin Health %", f"{margin_kpi}%")

    st.divider()

    # -----------------------------
    # ROLE-BASED VIEWS
    # -----------------------------
    if role == "Delivery Head":
        st.subheader("🚨 Delivery Risk Projects")
        st.dataframe(result["risk_projects"], use_container_width=True)

        st.subheader("📉 Underutilized Employees")
        st.dataframe(result["low_util"], use_container_width=True)

    elif role == "HR":
        st.subheader("⚠️ HR Risk Employees")
        st.dataframe(result["hr_risks"], use_container_width=True)

    elif role == "Finance":
        st.subheader("💰 Loss / Margin Risk Projects")
        st.dataframe(result["loss_projects"], use_container_width=True)

    # -----------------------------
    # EXECUTIVE SUMMARY
    # -----------------------------
    st.subheader("🧠 Executive AI Summary")
    st.success(explanation)

    pdf_path = generate_pdf(
        explanation,
        {"util": util_kpi, "risk": risk_kpi, "margin": margin_kpi}
    )

    with open(pdf_path, "rb") as f:
        st.download_button(
            "📄 Download Executive PDF Report",
            f,
            file_name="Delivery_Intelligence_Report.pdf",
            mime="application/pdf"
        )

# ===============================
# CHATBOT
# ===============================
st.markdown("---")
st.subheader("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask about teams, utilization, delivery risk, HR or margin"
)

if st.button("🧠 Get Answer"):
    if question.strip():
        st.success(
            answer_question(
                question,
                data,
                util_df,
                risk_df,
                cost_df,
                hr_df
            )
        )
    else:
        st.warning("Please enter a question.")

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
