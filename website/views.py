from django.shortcuts import render
from .forms import LinkCheckForm
import base64
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import check_url_with_virustotal, extract_domain
from whatsapp_verifier.models import FederalProgram
from .utils_chatbot import query_openrouter, search_programs_in_db
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from .models import ScamReport 
import json
from django.conf import settings
from .forms import ScamReportForm
import requests
# Create your views here.


@csrf_exempt
def api_report_scam(request):
    if request.method == "POST":
        data = json.loads(request.body)

        ScamReport.objects.create(
            initiative_type=data.get("initiative_type"),
            reference=data.get("reference"),
            description=data.get("description"),
            contact=data.get("contact"),
            platforms=",".join(data.get("platform", []))
        )

        return JsonResponse({"status": "success"})
    
    return JsonResponse({"error": "Invalid request"}, status=400)


def landing_page(request):
    return render(request, "website/landing.html")

def verify_link(request):
    result = None
    form = LinkCheckForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        original_url = form.cleaned_data["url"]

        # --- VirusTotal check (inline) ---
        try:
            headers = {
                "x-apikey": settings.VIRUSTOTAL_API_KEY
            }
            
            # Encode URL for VirusTotal API
            url_id = base64.urlsafe_b64encode(original_url.encode()).decode().strip("=")
            
            # Correct VirusTotal API endpoint
            vt_response = requests.get(
                f"https://www.virustotal.com/api/v3/urls/{url_id}",
                headers=headers
            )
            
            if vt_response.status_code == 200:
                vt_data = vt_response.json()
                
                # Extract detailed scan results
                attributes = vt_data.get('data', {}).get('attributes', {})
                stats = attributes.get('last_analysis_stats', {})
                results = attributes.get('last_analysis_results', {})
                
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                
                vt_safe = malicious == 0 and suspicious == 0
                
                # Categorize threats by type
                threat_types = {
                    'phishing': 0,
                    'malware': 0,
                    'spam': 0,
                    'scam': 0,
                    'suspicious': 0,
                    'other_malicious': 0
                }
                
                threat_details = []
                
                for engine, result in results.items():
                    category = result.get('category', '').lower()
                    result_text = result.get('result', '').lower()
                    
                    if category in ['malicious', 'suspicious']:
                        # Categorize by threat type
                        if 'phishing' in result_text or 'phish' in result_text:
                            threat_types['phishing'] += 1
                            threat_details.append({'engine': engine, 'type': 'Phishing', 'result': result.get('result', 'Phishing detected')})
                        elif 'malware' in result_text or 'trojan' in result_text or 'virus' in result_text:
                            threat_types['malware'] += 1
                            threat_details.append({'engine': engine, 'type': 'Malware', 'result': result.get('result', 'Malware detected')})
                        elif 'spam' in result_text:
                            threat_types['spam'] += 1
                            threat_details.append({'engine': engine, 'type': 'Spam', 'result': result.get('result', 'Spam detected')})
                        elif 'scam' in result_text or 'fraud' in result_text:
                            threat_types['scam'] += 1
                            threat_details.append({'engine': engine, 'type': 'Scam/Fraud', 'result': result.get('result', 'Scam detected')})
                        elif category == 'suspicious':
                            threat_types['suspicious'] += 1
                            threat_details.append({'engine': engine, 'type': 'Suspicious', 'result': result.get('result', 'Suspicious activity')})
                        else:
                            threat_types['other_malicious'] += 1
                            threat_details.append({'engine': engine, 'type': 'Other Threat', 'result': result.get('result', 'Threat detected')})
                
                # Determine primary threat type
                primary_threat = None
                if threat_types['phishing'] > 0:
                    primary_threat = 'phishing'
                elif threat_types['malware'] > 0:
                    primary_threat = 'malware'
                elif threat_types['scam'] > 0:
                    primary_threat = 'scam'
                elif threat_types['spam'] > 0:
                    primary_threat = 'spam'
                elif threat_types['suspicious'] > 0:
                    primary_threat = 'suspicious'
                elif threat_types['other_malicious'] > 0:
                    primary_threat = 'other'
                
                vt_result = {
                    "safe": vt_safe,
                    "primary_threat": primary_threat,
                    "threat_types": threat_types,
                    "threat_details": threat_details,
                    "total_threats": sum(threat_types.values()),
                    "scan_date": attributes.get('last_analysis_date'),
                    "reputation": attributes.get('reputation', 0),
                    "url": attributes.get('url', original_url)
                }
            else:
                vt_result = {
                    "error": f"VirusTotal API error {vt_response.status_code}",
                    "details": vt_response.text,
                    "safe": None
                }
        except Exception as e:
            vt_result = {
                "error": f"Error checking with VirusTotal: {str(e)}",
                "safe": None
            }

        # Extract domain from input
        domain = extract_domain(original_url)

        # Match domain against FederalProgram.link field
        program = FederalProgram.objects.filter(link__icontains=domain).first()

        result = {
            "safe_browsing": vt_result,  # Changed from "virustotal" to match template
            "program": program,
        }

    return render(request, "website/verify_link.html", {
        "form": form,
        "result": result,
    })

def report_scam(request):
    if request.method == 'POST':
        form = ScamReportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            # ✅ Redirect to thank-you page after saving
            return redirect('thank_you')
        else:
            messages.error(request, "There was an error with your submission. Please check the form.")
    else:
        form = ScamReportForm()
    
    return render(request, 'website/report_scam.html', {'form': form})

def thank_you(request):
    return render(request, 'website/thank_you.html')

def initiatives(request):
    programs = FederalProgram.objects.all().order_by('name')
    return render(request, "website/initiatives.html", {"programs": programs})

def resources(request):
    return render(request, "website/resources.html")


@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")

        # User bubble
        user_html = f"""
        <div class="flex justify-end mb-2">
            <div class="bg-green-600 text-white p-3 rounded-2xl max-w-xs shadow text-sm">
                {user_message}
            </div>
        </div>
        """

        # DB search
        programs = search_programs_in_db(user_message)
        db_reply = ""
        if programs.exists():
            db_reply += "<p class='font-semibold mb-1'>✅ Related programs:</p>"
            for p in programs:
                db_reply += f"<div class='mb-2 text-sm'><strong>{p.name}</strong> ({p.agency})<br>{p.description}</div>"
        else:
            db_reply = "<p class='text-gray-600 text-sm'>ℹ️ No direct matches in the database.</p>"

        # AI reply
        ai_reply = query_openrouter(user_message)

        # Bot bubble
        bot_html = f"""
        <div class="flex justify-start mb-4">
            <div class="bg-gray-200 text-gray-900 p-3 rounded-2xl max-w-xs shadow text-sm">
                {db_reply}
                <div class="mt-2 text-gray-800">{ai_reply}</div>
            </div>
        </div>
        """

        return HttpResponse(user_html + bot_html)

    return render(request, "website/chatbot.html")