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
import httpx

def explain_insight(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "LLM unavailable: GROQ_API_KEY not set"

    try:
        # IMPORTANT: trust_env=False disables Streamlit proxies
        with httpx.Client(timeout=20, trust_env=False) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                },
            )

        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LLM unavailable: {e}"

    except Exception as e:
        return f"LLM unavailable: {e}"

