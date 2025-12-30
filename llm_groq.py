import os
from groq import Groq
from dotenv import load_dotenv

# Load env only for local development
load_dotenv()

def explain_insight(prompt: str) -> str:
    try:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return "LLM unavailable: GROQ_API_KEY not set"

        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=20
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM unavailable: {e}"
