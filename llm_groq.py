import os
import httpx

def explain_insight(prompt: str) -> str | None:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return None

    try:
        with httpx.Client(timeout=15, trust_env=False) as client:
            response = client.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                },
            )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception:
        return None
