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
# SIDEBAR
# ===============================
st.sidebar.image("compunnel_logo.jpg", use_column_width=True)
st.sidebar.header("📂 Upload Delivery Data")

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV / Excel",
    type=["csv", "xlsx"]
)

# ===============================
# LOAD DATA
# ===============================
def load_data(file):
    if file is None:
        st.stop()

    if file.name.endswith(".csv"):
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
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
# CHAT UI
# ===============================
st.title("🤖 Ask Delivery Intelligence Bot")

question = st.text_input(
    "Ask about teams, utilization, delivery risk, HR or margin"
)

if st.button("🧠 Get Answer"):
    with st.spinner("Analyzing..."):
        result = answer_question(
            question,
            data,
            util_df,
            risk_df,
            cost_df,
            hr_df
        )

    # 🔴 THIS IS THE CRITICAL FIX
    if isinstance(result, pd.DataFrame):
        st.subheader("📋 Result")
        st.dataframe(result, use_container_width=True)
    elif isinstance(result, str):
        st.success(result)
    else:
        st.error("Unexpected response type.")

st.markdown("---")
st.caption("© 2026 Compunnel Digital | Agentic AI – Delivery Intelligence")
