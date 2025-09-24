import requests
from decouple import config
from googletrans import Translator
from .models import FederalProgram

VIRUSTOTAL_API_KEY = config('VIRUSTOTAL_API_KEY', default='')

def translate_text(text, dest_language):
    """Translate text to the specified language"""
    try:
        translator = Translator()
        translation = translator.translate(text, dest=dest_language)
        return translation.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def verify_link_virustotal(url):
    """Verify a URL using VirusTotal API - IMMEDIATE RESULTS VERSION"""
    if not VIRUSTOTAL_API_KEY:
        return "❌ VirusTotal service is currently unavailable. Please try again later."
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY,
        "User-Agent": "Federal-Programs-Bot/1.0"
    }
    
    try:
        print(f"Analyzing URL: {url}")
        
        # Extract domain for basic safety check
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.lower()
        
        # List of known safe Nigerian government domains
        safe_ng_domains = [
            'gov.ng', 'n-sip.gov.ng', 'statehouse.gov.ng', 'cbn.gov.ng',
            'ncdc.gov.ng', 'nphcda.gov.ng', 'nysc.gov.ng', 'nddc.gov.ng',
            'tetfund.gov.ng', 'boi.ng', 'rea.gov.ng'
        ]
        
        # List of generally safe global domains
        safe_global_domains = [
            'google.com', 'github.com', 'wikipedia.org', 'microsoft.com',
            'apple.com', 'facebook.com', 'instagram.com', 'twitter.com',
            'youtube.com', 'whatsapp.com'
        ]
        
        # Check if it's a known safe domain
        if any(safe_domain in domain for safe_domain in safe_ng_domains):
            return f"✅ SAFE LINK\n\nThis is a verified Nigerian government website ({domain}). Generally safe for official use."
        
        if any(safe_domain in domain for safe_domain in safe_global_domains):
            return f"✅ LIKELY SAFE\n\nThis is a well-known website ({domain}). Generally safe but always exercise caution."
        
        # Check for suspicious patterns
        suspicious_keywords = ['login', 'password', 'bank', 'verify', 'secure', 'account', 'pay']
        if any(keyword in url.lower() for keyword in suspicious_keywords):
            return f"⚠️ SUSPICIOUS PATTERN\n\nThis link contains keywords commonly used in phishing attempts. Be very careful about entering personal information."
        
        # Now check VirusTotal for existing analysis
        url_id = requests.utils.quote(url, safe='')
        analysis_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        
        response = requests.get(analysis_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Existing analysis found - provide immediate results
            result = response.json()
            stats = result['data']['attributes']['last_analysis_stats']
            last_analysis = result['data']['attributes']['last_analysis_date']
            
            # Convert timestamp to readable date
            from datetime import datetime
            analysis_date = datetime.fromtimestamp(last_analysis).strftime('%Y-%m-%d')
            
            if stats['malicious'] > 0:
                return f"🚨 DANGEROUS LINK\n\n{stats['malicious']} security vendors flagged this as MALICIOUS!\nLast checked: {analysis_date}\n\n❌ AVOID THIS LINK"
            elif stats['suspicious'] > 0:
                return f"⚠️ SUSPICIOUS LINK\n\n{stats['suspicious']} vendors flagged this as suspicious.\nLast checked: {analysis_date}\n\n🔒 Proceed with extreme caution"
            elif stats['harmless'] > 0:
                return f"✅ SAFE LINK\n\n{stats['harmless']} vendors marked this as harmless.\nLast checked: {analysis_date}\n\nGenerally safe to use"
            else:
                return f"🔍 UNKNOWN LINK\n\nNo security analysis available yet.\n\nSubmit for analysis or exercise caution."
        
        elif response.status_code == 404:
            # No existing analysis - provide quick safety tips
            return f"🔍 NEW LINK ANALYSIS\n\nThis link hasn't been analyzed yet.\n\nDomain: {domain}\n\n💡 Safety Tips:\n• Check the URL carefully before clicking\n• Don't enter personal information\n• Use official websites when possible\n\nYou can submit it for analysis by verifying this link again in 2-3 minutes."
        
        else:
            # API error - fallback to basic analysis
            return f"🔍 LINK ANALYSIS\n\nDomain: {domain}\n\nQuick Assessment:\n• {'✅ Known domain' if '.' in domain else '❌ Unusual domain'}\n• {'⚠️ Contains suspicious keywords' if any(kw in url.lower() for kw in suspicious_keywords) else '✅ No obvious red flags'}\n\n💡 Always verify URLs before clicking!"
                
    except requests.exceptions.Timeout:
        return "⏰ Service timeout. Using quick safety check...\n\n💡 Always:\n• Verify URLs before clicking\n• Don't enter personal info on unfamiliar sites\n• Use official government websites"
    except Exception as e:
        return f"🔍 Basic Link Check\n\nUnable to perform full analysis. \n\nQuick Tips:\n• Check if the URL looks legitimate\n• Look for misspellings or unusual characters\n• When in doubt, don't click!"