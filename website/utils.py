import requests
from decouple import config
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

# Google Safe Browsing API key
GOOGLE_SAFE_BROWSING_KEY = config("GOOGLE_SAFE_BROWSING_KEY", default="")

def check_url_with_google_safe_browsing(url: str) -> dict:
    """
    Check a URL against Google Safe Browsing API.
    Returns dict with 'safe', 'error', or 'details'.
    """
    # Debug: Check if API key is loaded
    if not GOOGLE_SAFE_BROWSING_KEY:
        logger.error("GOOGLE_SAFE_BROWSING_KEY is empty or not set")
        return {"error": "API key not configured"}
    
    logger.info(f"API Key length: {len(GOOGLE_SAFE_BROWSING_KEY)}")
    logger.info(f"Checking URL: {url}")

    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_KEY}"

    payload = {
        "client": {
            "clientId": "gds-verified-schemes",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(api_url, json=payload, timeout=10)
        logger.info(f"API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if "matches" in data:
                return {"safe": False, "details": data["matches"]}
            return {"safe": True}
        elif response.status_code == 401:
            logger.error(f"Google Safe Browsing API 401 Error: {response.text}")
            return {"error": "Invalid API key - please check configuration"}
        else:
            logger.error(f"Google Safe Browsing API Error {response.status_code}: {response.text}")
            return {"error": f"API request failed ({response.status_code})"}
    except Exception as e:
        logger.error(f"Google Safe Browsing API Exception: {str(e)}")
        return {"error": str(e)}

def extract_domain(url: str) -> str:
    """
    Extracts and cleans the domain name from a URL.
    Example:
        https://www.nirsal.gov.ng/programs/loan -> nirsal.gov.ng
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        # Strip leading "www."
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    except Exception:
        return url.lower()