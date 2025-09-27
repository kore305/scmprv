from django.shortcuts import render
from .forms import LinkCheckForm
import base64
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .utils import check_url_with_virustotal, extract_domain
from whatsapp_verifier.models import FederalProgram
from .utils_chatbot import query_openrouter, search_programs_in_db
from django.shortcuts import render
from django.conf import settings
import requests
# Create your views here.

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
                vt_result = vt_response.json()
                # Check if URL is safe based on VirusTotal response
                stats = vt_result.get('data', {}).get('attributes', {}).get('last_analysis_stats', {})
                malicious = stats.get('malicious', 0)
                suspicious = stats.get('suspicious', 0)
                
                vt_safe = malicious == 0 and suspicious == 0
                vt_result = {
                    "safe": vt_safe,
                    "malicious_count": malicious,
                    "suspicious_count": suspicious,
                    "full_response": vt_result
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
    return render(request, "website/report_scam.html")

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