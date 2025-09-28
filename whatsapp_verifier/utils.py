import requests
import base64
import hashlib
from urllib.parse import urlparse
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

def get_program_info(program_name, language='en'):
    """Get information about a federal program"""
    try:
        # Try to find the program in the database
        program = FederalProgram.objects.filter(name__icontains=program_name).first()
        
        if program:
            message = f"✅ PROGRAM FOUND\n\n📋 Name: {program.name}\n🏢 Sector: {program.sector}\n🔗 Official Link: {program.link}"
            if program.description:
                message += f"\n📝 Description: {program.description}"
        else:
            # If not found in database, provide general guidance
            message = f"❌ PROGRAM NOT FOUND\n\n'{program_name}' was not found in our database.\n\n💡 Tips:\n• Check spelling\n• Try shorter name (e.g., 'N-Power' instead of 'N-Power Program')\n• Contact relevant ministry directly\n\n🏛️ Common Programs:\n• N-Power\n• Anchor Borrowers\n• TraderMoni\n• MarketMoni\n• Conditional Cash Transfer"
        
        # Translate if needed
        if language != 'en':
            message = translate_text(message, language)
            
        return message
        
    except Exception as e:
        print(f"Error getting program info: {e}")
        base_message = f"⚠️ Error retrieving information for '{program_name}'. Please try again or contact support."
        if language != 'en':
            return translate_text(base_message, language)
        return base_message

def get_url_id_base64(url):
    """Get base64 URL identifier for VirusTotal API (without padding)"""
    try:
        # Canonicalize URL (basic version)
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        # Remove trailing slash if present
        if url.endswith('/') and len(url) > 8:  # Don't remove from just http:// or https://
            url = url.rstrip('/')
        
        # Encode to base64 and remove padding
        url_bytes = url.encode('utf-8')
        base64_encoded = base64.urlsafe_b64encode(url_bytes).decode('utf-8')
        # Remove padding characters
        url_id = base64_encoded.rstrip('=')
        return url_id
    except Exception as e:
        print(f"Error creating URL ID: {e}")
        return None

def get_url_id_sha256(url):
    """Get SHA-256 URL identifier for VirusTotal API"""
    try:
        # Canonicalize URL (basic version)
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Remove trailing slash if present
        if url.endswith('/') and len(url) > 8:
            url = url.rstrip('/')
        
        # Create SHA-256 hash
        url_bytes = url.encode('utf-8')
        sha256_hash = hashlib.sha256(url_bytes).hexdigest()
        return sha256_hash
    except Exception as e:
        print(f"Error creating SHA-256 URL ID: {e}")
        return None

def basic_url_safety_check(url):
    """Perform basic safety checks without API"""
    try:
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # List of known safe Nigerian government domains
        safe_ng_domains = [
            'gov.ng', 'n-sip.gov.ng', 'statehouse.gov.ng', 'cbn.gov.ng',
            'ncdc.gov.ng', 'nphcda.gov.ng', 'nysc.gov.ng', 'nddc.gov.ng',
            'tetfund.gov.ng', 'boi.ng', 'rea.gov.ng', 'npc.gov.ng'
        ]
        
        # List of generally safe global domains
        safe_global_domains = [
            'google.com', 'github.com', 'wikipedia.org', 'microsoft.com',
            'apple.com', 'facebook.com', 'instagram.com', 'twitter.com',
            'youtube.com', 'whatsapp.com', 'linkedin.com'
        ]
        
        # Check if it's a known safe domain
        if any(safe_domain in domain for safe_domain in safe_ng_domains):
            return f"✅ GOVERNMENT WEBSITE\n\nDomain: {domain}\nThis appears to be an official Nigerian government website. Generally safe for official use.\n\n🔒 Always verify the exact URL spelling before entering personal information."
        
        if any(safe_domain in domain for safe_domain in safe_global_domains):
            return f"✅ KNOWN WEBSITE\n\nDomain: {domain}\nThis is a well-known website. Generally safe but always exercise caution.\n\n💡 Verify you're on the correct official website."
        
        # Check for suspicious patterns
        suspicious_keywords = ['login', 'password', 'bank', 'verify', 'secure', 'account', 'pay', 'update', 'confirm']
        suspicious_found = [kw for kw in suspicious_keywords if kw in url.lower()]
        
        if suspicious_found:
            return f"⚠️ SUSPICIOUS PATTERNS DETECTED\n\nDomain: {domain}\nSuspicious keywords found: {', '.join(suspicious_found)}\n\n🚨 BE VERY CAREFUL:\n• This link contains words commonly used in phishing\n• Don't enter personal/financial information\n• Verify with official sources"
        
        # Check for suspicious domain patterns
        if any(char in domain for char in ['xn--', '..', '--']):
            return f"⚠️ SUSPICIOUS DOMAIN\n\nDomain: {domain}\nThis domain contains potentially suspicious patterns.\n\n🔍 Double-check the spelling and authenticity"
        
        return f"🔍 UNKNOWN WEBSITE\n\nDomain: {domain}\n\n💡 SAFETY TIPS:\n• Verify the website is legitimate\n• Check for spelling errors in the URL\n• Don't enter personal information unless certain\n• When in doubt, contact the organization directly"
        
    except Exception as e:
        return f"❌ URL ANALYSIS ERROR\n\nCould not analyze the URL properly.\n\n💡 Manual check recommended:\n• Verify URL spelling\n• Check for suspicious characters\n• Only visit trusted websites"

def verify_link_virustotal(url):
    """Verify a URL using VirusTotal API with proper error handling"""
    print(f"🔍 Starting analysis for: {url}")
    
    # Always perform basic safety check first
    basic_result = basic_url_safety_check(url)
    
    # If no API key, return basic check only
    if not VIRUSTOTAL_API_KEY:
        return f"⚠️ VirusTotal API unavailable\n\n{basic_result}"
    
    # Validate and normalize URL
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    headers = {
        "x-apikey": VIRUSTOTAL_API_KEY,
        "User-Agent": "Federal-Programs-Bot/1.0"
    }
    
    try:
        # Create proper URL identifier using base64 encoding
        url_id = get_url_id_base64(url)
        if not url_id:
            return f"❌ URL Processing Error\n\n{basic_result}"
        
        print(f"🔗 URL ID (base64): {url_id[:20]}...")
        
        # Try to get existing analysis first
        analysis_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        
        print(f"📡 Making API request to: {analysis_url}")
        response = requests.get(analysis_url, headers=headers, timeout=15)
        
        print(f"📊 API Response Status: {response.status_code}")
        
        if response.status_code == 200:
            # Existing analysis found
            result = response.json()
            
            if 'data' not in result or 'attributes' not in result['data']:
                return f"⚠️ API Response Format Error\n\n{basic_result}"
            
            attributes = result['data']['attributes']
            
            if 'last_analysis_stats' not in attributes:
                return f"🔍 NO ANALYSIS DATA\n\nURL hasn't been fully analyzed yet.\n\n{basic_result}"
            
            stats = attributes['last_analysis_stats']
            last_analysis = attributes.get('last_analysis_date', 0)
            
            # Convert timestamp to readable date if available
            analysis_date = "Unknown"
            if last_analysis:
                try:
                    from datetime import datetime
                    analysis_date = datetime.fromtimestamp(last_analysis).strftime('%Y-%m-%d %H:%M')
                except:
                    analysis_date = "Recent"
            
            # Analyze results
            malicious = stats.get('malicious', 0)
            suspicious = stats.get('suspicious', 0)
            harmless = stats.get('harmless', 0)
            undetected = stats.get('undetected', 0)
            
            total_scans = malicious + suspicious + harmless + undetected
            
            if malicious > 0:
                return f"🚨 DANGEROUS LINK DETECTED!\n\n⚠️ {malicious}/{total_scans} security vendors flagged this as MALICIOUS\nLast analysis: {analysis_date}\n\n⛔ DO NOT VISIT THIS LINK\n⛔ DO NOT ENTER ANY INFORMATION\n\n{basic_result}"
            
            elif suspicious > 0:
                return f"⚠️ SUSPICIOUS LINK\n\n🟡 {suspicious}/{total_scans} vendors flagged as suspicious\nLast analysis: {analysis_date}\n\n🔒 PROCEED WITH EXTREME CAUTION:\n• Don't enter personal information\n• Verify website legitimacy first\n\n{basic_result}"
            
            elif harmless > 0:
                return f"✅ LINK APPEARS SAFE\n\n✓ {harmless}/{total_scans} vendors marked as harmless\nLast analysis: {analysis_date}\n\n{basic_result}"
            
            else:
                return f"🔍 INCONCLUSIVE RESULTS\n\nScanned by {total_scans} vendors\nLast analysis: {analysis_date}\n\n{basic_result}"
        
        elif response.status_code == 404:
            # URL not found in VirusTotal database - submit for analysis
            print("📤 URL not found, attempting to submit for analysis...")
            
            # Submit URL for analysis
            submit_url = "https://www.virustotal.com/api/v3/urls"
            submit_data = {"url": url}
            
            submit_response = requests.post(submit_url, headers=headers, data=submit_data, timeout=15)
            
            if submit_response.status_code == 200:
                return f"🔍 ANALYSIS SUBMITTED\n\nURL submitted to VirusTotal for analysis.\n\n⏱️ Results will be available in 1-2 minutes.\nTry verifying again shortly.\n\n{basic_result}"
            else:
                return f"🔍 NEW URL\n\nThis URL hasn't been analyzed by VirusTotal yet.\n\n{basic_result}"
        
        elif response.status_code == 401:
            return f"🔑 API KEY ERROR\n\nVirusTotal API key is invalid or expired.\n\n{basic_result}"
        
        elif response.status_code == 429:
            return f"⏰ RATE LIMIT EXCEEDED\n\nToo many requests. Please wait a moment and try again.\n\n{basic_result}"
        
        else:
            print(f"❌ Unexpected API response: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:200]}")
            
            return f"⚠️ API ERROR (Status: {response.status_code})\n\nUsing basic safety analysis:\n\n{basic_result}"
                
    except requests.exceptions.Timeout:
        return f"⏰ SERVICE TIMEOUT\n\nVirusTotal service is slow. Using basic analysis:\n\n{basic_result}"
    
    except requests.exceptions.ConnectionError:
        return f"🌐 CONNECTION ERROR\n\nCannot reach VirusTotal. Using basic analysis:\n\n{basic_result}"
    
    except Exception as e:
        print(f"❌ Unexpected error in verify_link_virustotal: {e}")
        return f"❌ ANALYSIS ERROR\n\nUnexpected error occurred. Using basic analysis:\n\n{basic_result}"