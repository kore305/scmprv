import requests
from decouple import config
from urllib.parse import urlparse
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Google Safe Browsing API key
VIRUSTOTAL_API_KEY = config("VIRUSTOTAL_API_KEY", default="")

def check_url_with_virustotal(url):
    headers = {
        "x-apikey": settings.VIRUSTOTAL_API_KEY
    }
    response = requests.get(
        f"https://www.virustotal.com/api/v3/urls/{url}",
        headers=headers
    )
    if response.status_code == 200:
        return response.json()
    return {"error": "Failed to fetch data from VirusTotal"}

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