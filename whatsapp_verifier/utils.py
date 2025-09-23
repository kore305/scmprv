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
    """Verify a URL using VirusTotal API - FIXED VERSION"""
    if not VIRUSTOTAL_API_KEY:
        return "❌ VirusTotal API key not configured. Please contact administrator."
    
    # Validate URL format
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        print(f"Analyzing URL: {url}")
        
        # Step 1: Submit URL for analysis
        submit_url = "https://www.virustotal.com/api/v3/urls"
        payload = {"url": url}
        
        response = requests.post(submit_url, headers=headers, data=payload, timeout=30)
        print(f"Submit response: {response.status_code}")
        
        if response.status_code == 200:
            # URL submitted successfully, get analysis ID
            result = response.json()
            analysis_id = result['data']['id']
            print(f"Analysis ID: {analysis_id}")
            
            return "✅ Link submitted for analysis. This may take a few minutes. Please check back later."
            
        elif response.status_code == 400:
            # URL might already exist in database, try to get existing analysis
            print("URL may already exist, trying to get existing analysis...")
            url_id = requests.utils.quote(url, safe='')
            analysis_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            
            analysis_response = requests.get(analysis_url, headers=headers, timeout=30)
            
            if analysis_response.status_code == 200:
                result = analysis_response.json()
                stats = result['data']['attributes']['last_analysis_stats']
                
                if stats['malicious'] > 0:
                    return f"🚨 DANGEROUS LINK: {stats['malicious']} security vendors flagged this as malicious. Avoid this link!"
                elif stats['suspicious'] > 0:
                    return f"⚠️ SUSPICIOUS LINK: {stats['suspicious']} vendors flagged this as suspicious. Proceed with caution."
                else:
                    return f"✅ SAFE LINK: {stats['harmless']} vendors marked this as harmless. {stats['undetected']} undetected."
            else:
                return "❌ Unable to analyze this link. Please try a different URL."
                
        else:
            return f"❌ VirusTotal API error: {response.status_code}. Please try again later."
            
    except requests.exceptions.Timeout:
        return "⏰ Analysis timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        return f"❌ Network error: {str(e)}"
    except Exception as e:
        return f"❌ Unexpected error: {str(e)}"

def get_program_info(program_name, language='en'):
    """Get information about a federal program"""
    try:
        program = FederalProgram.objects.get(name__icontains=program_name)
        message = f"✅ {program.name} is verified.\n📊 Sector: {program.sector}\n🏢 Agency: {program.agency}\n🔗 More info: {program.link}"
        
        if language != 'en':
            message = translate_text(message, language)
            
        return message
    except FederalProgram.DoesNotExist:
        base_message = f"❌ Program '{program_name}' not found. Please check spelling or try:\n- N-Power\n- Anchor Borrowers\n- Conditional Cash Transfer"
        if language != 'en':
            return translate_text(base_message, language)
        return base_message
    except FederalProgram.MultipleObjectsReturned:
        programs = FederalProgram.objects.filter(name__icontains=program_name)[:5]
        base_message = f"🔍 Multiple programs found. Please be specific:\n" + "\n".join([f"- {p.name}" for p in programs])
        if language != 'en':
            return translate_text(base_message, language)
        return base_message