import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

from groq import Groq
import os

def get_llm():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


# def explain_insight(prompt: str) -> str:
#     try:
#         client = Groq(api_key=os.getenv("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"))
#         response = client.chat.completions.create(
#             model="llama-3.1-8b-instant",
#             messages=[{"role": "user", "content": prompt}],
#             timeout=10
#         )
#         return response.choices[0].message.content
#     except Exception as e:
#         return f"LLM unavailable: {e}"

