import os
import httpx

def explain_insight(prompt: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return "❌ LLM Error: GROQ_API_KEY not loaded"

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
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                },
            )

        if response.status_code == 401:
            return "❌ LLM Error: Invalid API Key (Groq rejected the key)"

        if response.status_code != 200:
            return f"❌ LLM Error: HTTP {response.status_code} – {response.text}"

        data = response.json()

        if "choices" not in data:
            return f"❌ LLM Error: Unexpected response format – {data}"

        return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"❌ LLM Exception: {str(e)}"
