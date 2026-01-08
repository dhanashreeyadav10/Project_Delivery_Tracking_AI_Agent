import streamlit as st
from groq import Groq


def explain_insight(prompt: str) -> str:
    try:
        # ✅ Correct way to read Streamlit secrets
        api_key = st.secrets["GROQ_API_KEY"]

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a senior enterprise delivery intelligence advisor."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            timeout=15
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ LLM unavailable: {str(e)}"
