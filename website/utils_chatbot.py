import os
import requests

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

def query_openrouter(message, language="en"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://scmprv-production.up.railway.app",   # ✅ required
        "X-Title": "GDS Verified Schemes Chatbot", # ✅ required
        "Content-Type": "application/json",
    }

    system_prompt = f"""
    You are GDS Verified Schemes chatbot. 
    Reply in the same language as the user (supports English, Igbo, Hausa, Yoruba).
    Be helpful, concise, and factually correct.
    """

    payload = {
        "model": "openai/gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        return f"⚠️ Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"⚠️ Error: {str(e)}"
