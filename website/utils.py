import requests
from decouple import config
from urllib.parse import urlparse
import logging
import base64
from django.conf import settings

logger = logging.getLogger(__name__)

# Google Safe Browsing API key
VIRUSTOTAL_API_KEY = config("VIRUSTOTAL_API_KEY", default="")

def check_url_with_virustotal(url: str):
    """
    Submit a URL to VirusTotal and return the scan results.
    """
    headers = {
        "x-apikey": settings.VIRUSTOTAL_API_KEY
    }

    # Encode URL for lookup (strip '=' padding)
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    # Query VirusTotal
    response = requests.get(
        f"https://www.virustotal.com/api/v3/urls{url}",
        headers=headers
    )

    if response.status_code == 200:
        return response.json()
    else:
        return {
            "error": f"VirusTotal API error {response.status_code}",
            "details": response.text,
        }
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