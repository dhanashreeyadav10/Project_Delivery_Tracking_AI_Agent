import os
import httpx


def explain_insight(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "LLM unavailable: GROQ_API_KEY not set"

    try:
        with httpx.Client(timeout=30, trust_env=False) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": "You are an enterprise delivery intelligence advisor."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                },
            )

        # ❗ Check HTTP failure
        if response.status_code != 200:
            return f"LLM unavailable: HTTP {response.status_code}"

        data = response.json()

        # ❗ Defensive check
        if "choices" not in data or not data["choices"]:
            return "LLM unavailable: empty response from model"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"LLM unavailable: {str(e)}"
