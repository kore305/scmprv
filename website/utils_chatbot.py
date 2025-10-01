import requests
from decouple import config
from whatsapp_verifier.models import FederalProgram

OPENROUTER_API_KEY = config("OPENROUTER_API_KEY")


def query_openrouter(message, language="en"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    # Updated headers for OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://safecheck.up.railway.app/",
        "X-Title": "GDS Verified Schemes Chatbot",
    }

    system_prompt = f"""
    Your name is Ana.
You are the GDS Verified Schemes chatbot for Nigeria.
You were built to assist Nigerian citizens with information about government schemes and programs.

LANGUAGE: Reply in the same language as the user. Supported languages: English, Igbo, Hausa, Yoruba.

BEHAVIOR:
- Be helpful, concise, and factually correct
- Focus exclusively on Nigerian government schemes, programs, and social interventions
- If a user enters letters/acronyms (e.g., "NSIP", "CCT", "GEEP"), treat them as government scheme acronyms and search for relevant information
- Use web search when needed to provide accurate, up-to-date information about schemes

SCOPE LIMITATIONS:
- Only answer questions related to Nigerian government schemes, social programs, registration processes, eligibility criteria, and benefits
- If a user asks about topics unrelated to government schemes, politely respond: "I'm sorry, I can only help with questions about Nigerian government schemes and programs. Is there a specific government program you'd like to know about?"

RESPONSE STYLE:
- Keep responses clear and accessible
- Provide practical information (eligibility, how to apply, benefits, contact details when available)
- If uncertain about current information, use search to verify facts
    """

    # payload = {
    #     "model": "openai/gpt-4o-mini",
    #     "messages": [
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": message},
    #     ],
    #     "max_tokens": 500,  # Add token limit
    #     "temperature": 0.7,  # Add temperature for consistency
    # }

    payload = {
        "model": "x-ai/grok-4-fast:free:online",  # add :online to enable OpenRouter web-search plugin
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message},
        ],
        "max_tokens": 500,
        "temperature": 0.7,
    }


    try:
        # Debug: Check if API key exists
        if not OPENROUTER_API_KEY:
            return "⚠️ Error: OpenRouter API key not configured"
        
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        
        # Debug logging
        print(f"OpenRouter Response Status: {response.status_code}")
        print(f"OpenRouter Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        elif response.status_code == 401:
            return "⚠️ Error: Invalid OpenRouter API key. Please check your configuration."
        elif response.status_code == 402:
            return "⚠️ Error: Insufficient credits in OpenRouter account."
        elif response.status_code == 429:
            return "⚠️ Error: Rate limit exceeded. Please try again later."
        else:
            return f"⚠️ OpenRouter Error {response.status_code}: {response.text}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Error: Request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        return "⚠️ Error: Connection failed. Please check your internet connection."
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