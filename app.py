import streamlit as st
import pandas as pd

from models import (
    utilization_model,
    delivery_risk_model,
    cost_margin_model,
    hr_health_model
)
from qa_bot import answer_question

# ===============================
# PAGE CONFIG
# ===============================
st.set_page_config(
    page_title="Agentic AI – Delivery Intelligence",
    layout="wide"
)

# ===============================
# SIDEBAR – BRANDING & UPLOAD
# ===============================
st.sidebar.image("compunnel_logo.jpg", use_column_width=True)
st.sidebar.markdown("### 📂 Upload Delivery Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV / Excel",
    type=["csv", "xlsx"]
)

# ===============================
# MAIN UI (ALWAYS RENDER)
# ===============================
st.title("🤖 Ask Delivery Intelligence Bot")
st.caption("Ask about teams, utilization, delivery risk, HR or margin")

st.markdown("---")

# ===============================
# LOAD DATA SAFELY
# ===============================
data = None
if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        data.columns = (
            data.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
        )

        st.success("✅ Data uploaded successfully")

    except Exception as e:
        st.error("❌ Failed to load data")
        st.code(str(e))

# ===============================
# RUN MODELS ONLY IF DATA EXISTS
# ===============================
util_df = risk_df = cost_df = hr_df = None

if data is not None:
    try:
        util_df = utilization_model(data)
        risk_df = delivery_risk_model(data)
        cost_df = cost_margin_model(data)
        hr_df = hr_health_model(data)
    except Exception as e:
        st.error("❌ Error while running analysis models")
        st.code(str(e))

# ===============================
# CHAT INPUT (DISABLED IF NO DATA)
# ===============================
question = st.text_input(
    "💬 Ask a question",
    placeholder="e.g. Are there people likely to leave? If yes, list their name, employee id and team name",
    disabled=data is None
)

if st.button("🧠 Get Answer", disabled=data is None):
    with st.spinner("Analyzing..."):
        result = answer_question(
            question,
            data,
            util_df,
            risk_df,
            cost_df,
            hr_df
        )

    # ✅ SAFE RENDERING
    if isinstance(result, pd.DataFrame):
        st.subheader("📋 Result")
        st.dataframe(result, use_container_width=True)
    else:
        st.success(result)

# ===============================
# FOOTER
# ===============================
st.markdown("---")
st.caption("© 2026 Compunnel Digital | Agentic AI – Delivery Intelligence Platform")
