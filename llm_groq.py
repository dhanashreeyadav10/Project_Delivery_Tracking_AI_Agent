# import os
# from groq import Groq
# from dotenv import load_dotenv

# # Load env only for local development
# load_dotenv()

# def explain_insight(prompt: str) -> str:
#     try:
#         api_key = os.getenv("GROQ_API_KEY")

#         if not api_key:
#             return "LLM unavailable: GROQ_API_KEY not set"

#         client = Groq(api_key=api_key)

#         response = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[
#                 {"role": "user", "content": prompt}
#             ],
#             timeout=20
#         )

#         return response.choices[0].message.content

#     except Exception as e:
#         return f"LLM unavailable: {e}"


import os
from dotenv import load_dotenv
from groq import Groq

# Load .env locally (Streamlit ignores it anyway)
load_dotenv()

# -----------------------------------------
# 🔥 FORCE REMOVE PROXIES (CRITICAL)
# -----------------------------------------
for proxy_var in [
    "HTTP_PROXY", "HTTPS_PROXY",
    "http_proxy", "https_proxy",
    "ALL_PROXY"
]:
    os.environ.pop(proxy_var, None)

# -----------------------------------------
# LLM FUNCTION
# -----------------------------------------
def explain_insight(prompt: str) -> str:
    try:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return "LLM unavailable: GROQ_API_KEY not set"

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            timeout=20
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM unavailable: {e}"
