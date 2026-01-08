import streamlit as st
import pandas as pd
import io
import re
import chardet
import pdfplumber

# ===============================
# INTERNAL IMPORTS (UNCHANGED)
# ===============================
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
    "Upload Delivery Data (CSV / Excel / TXT / PDF)",
    type=["csv", "xlsx", "txt", "pdf"]
)

# ===============================
# SMART FILE LOADER (ALL TYPES)
# ===============================
def load_uploaded_data(file):
    if file is None:
        return None

    ext = file.name.lower().split(".")[-1]
    file_bytes = file.getvalue()

    try:
        # ---------- CSV ----------
        if ext == "csv":
            return pd.read_csv(io.BytesIO(file_bytes))

        # ---------- EXCEL ----------
        if ext == "xlsx":
            return pd.read_excel(io.BytesIO(file_bytes))

        # ---------- TXT ----------
        if ext == "txt":
            encoding = chardet.detect(file_bytes).get("encoding", "utf-8")
            text = file_bytes.decode(encoding, errors="ignore")

            for d in [",", ";", "\t", "|"]:
                if text.count(d) > 10:
                    return pd.read_csv(io.StringIO(text), sep=d)

            raise ValueError("Unable to detect delimiter in TXT file")

        # ---------- PDF ----------
        if ext == "pdf":
            rows = []
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if not text:
                        continue
                    for line in text.split("\n"):
                        parts = re.split(r"[,\t|]+", line.strip())
                        rows.append(parts)

            if not rows:
                raise ValueError("No tabular data found in PDF")

            return pd.DataFrame(rows)

    except Exception as e:
        st.error("❌ File parsing failed")
        st.code(str(e))
        return None

# ===============================
# MAIN UI (ALWAYS RENDERS)
# ===============================
st.title("🤖 Ask Delivery Intelligence Bot")
st.caption("Ask about teams, utilization, delivery risk, HR or margin")
st.markdown("---")

# ===============================
# LOAD DATA SAFELY
# ===============================
data = load_uploaded_data(uploaded_file)

if data is not None:
    # Normalize columns
    data.columns = (
        data.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    st.success("✅ Data uploaded successfully")

# ===============================
# RUN MODELS (ONLY IF DATA EXISTS)
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
# CHAT INPUT
# ===============================
question = st.text_input(
    "💬 Ask a question",
    placeholder="e.g. Are there people likely to leave? If yes, list their name, employee id and team name",
    disabled=data is None
)

if st.button("🧠 Get Answer", disabled=data is None):
    if not question.strip():
        st.warning("Please ask a question.")
    else:
        with st.spinner("Analyzing..."):
            result = answer_question(
                question,
                data,
                util_df,
                risk_df,
                cost_df,
                hr_df
            )

        # ===============================
        # CORRECT RENDERING (KEY FIX)
        # ===============================
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
