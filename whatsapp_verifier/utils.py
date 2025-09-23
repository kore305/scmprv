import requests
from decouple import config
from googletrans import Translator
from .models import FederalProgram

VIRUSTOTAL_API_KEY = config('VIRUSTOTAL_API_KEY', default='')

def translate_text(text, dest_language):
    """Translate text to the specified language"""
    translator = Translator()
    try:
        translation = translator.translate(text, dest=dest_language)
        return translation.text
    except:
        return text

def verify_link_virustotal(url):
    """Verify a URL using VirusTotal API"""
    if not VIRUSTOTAL_API_KEY:
        return "Error: VirusTotal API not configured"
    
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    url_id = requests.utils.quote(url, safe='')
    analysis_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    
    response = requests.get(analysis_url, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        stats = result['data']['attributes']['last_analysis_stats']
        return f"Link analysis: {stats['malicious']} malicious, {stats['suspicious']} suspicious, {stats['harmless']} harmless, {stats['undetected']} undetected"
    else:
        submit_url = "https://www.virustotal.com/api/v3/urls"
        payload = {"url": url}
        response = requests.post(submit_url, headers=headers, data=payload)
        
        if response.status_code == 200:
            return "Link submitted for analysis. Please check back later."
        else:
            return "Error analyzing link. Please try again later."

def get_program_info(program_name, language='en'):
    """Get information about a federal program"""
    try:
        program = FederalProgram.objects.get(name__icontains=program_name)
        message = f"{program.name} is verified. It is in the {program.sector} sector. Find more about it here: {program.link}"
        
        if language != 'en':
            message = translate_text(message, language)
            
        return message
    except FederalProgram.DoesNotExist:
        base_message = f"Program '{program_name}' not found in our database. Please check the spelling or try a different name."
        if language != 'en':
            return translate_text(base_message, language)
        return base_message
    except FederalProgram.MultipleObjectsReturned:
        programs = FederalProgram.objects.filter(name__icontains=program_name)
        base_message = f"Multiple programs found matching '{program_name}'. Please be more specific. Options: {', '.join([p.name for p in programs])}"
        if language != 'en':
            return translate_text(base_message, language)
        return base_message