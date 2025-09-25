from django.shortcuts import render
from .forms import LinkCheckForm
from .utils import check_url_with_google_safe_browsing, extract_domain
from whatsapp_verifier.models import FederalProgram
from .utils_chatbot import query_openrouter, search_programs_in_db
# Create your views here.

def landing_page(request):
    return render(request, "website/landing.html")

def verify_link(request):
    result = None
    form = LinkCheckForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        url = form.cleaned_data["url"]

        # Check with Google Safe Browsing
        safe_browsing_result = check_url_with_google_safe_browsing(url)

        # Extract domain from input
        domain = extract_domain(url)

        # Match domain against FederalProgram.link field
        program = FederalProgram.objects.filter(link__icontains=domain).first()

        result = {
            "safe_browsing": safe_browsing_result,
            "program": program,
        }

    return render(request, "website/verify_link.html", {
        "form": form,
        "result": result,
    })

def report_scam(request):
    return render(request, "website/report_scam.html")

def initiatives(request):
    return render(request, "website/initiatives.html")

def resources(request):
    return render(request, "website/resources.html")
@csrf_exempt
def chatbot(request):
    if request.method == "POST":
        user_message = request.POST.get("message", "")
        if not user_message:
            return JsonResponse({"reply": "Please type a message."})

        # First search database
        programs = search_programs_in_db(user_message)
        if programs.exists():
            reply = "Here are some programs I found:\n\n"
            for p in programs:
                reply += f"🔹 {p.name} ({p.agency})\n{p.description}\n\n"
            return JsonResponse({"reply": reply})

        # Else fallback to OpenRouter
        reply = query_openrouter(user_message)
        return JsonResponse({"reply": reply})

    return render(request, "website/chatbot.html")