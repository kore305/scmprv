import requests
from decouple import config
from whatsapp_verifier.models import FederalProgram

OPENROUTER_API_KEY = config("OPENROUTER_API_KEY")


def query_openrouter(message, language="en"):
    """
    Query OpenRouter API with multilingual support.
    """
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    system_prompt = f"""
    You are GDS Verified Schemes chatbot. 
    Reply in the same language as the user (supports English, Igbo, Hausa, Yoruba).
    Be helpful, concise, and factually correct.
    """

    payload = {
        "model": "openai/gpt-4o-mini",   # 🔑 multilingual & affordable
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


def search_programs_in_db(query):
    """
    Search for relevant programs in the FederalProgram database.
    Matches against name, description, or agency.
    """
    results = FederalProgram.objects.filter(
        name__icontains=query
    ) | FederalProgram.objects.filter(
        description__icontains=query
    ) | FederalProgram.objects.filter(
        agency__icontains=query
    )
    return results[:5]  