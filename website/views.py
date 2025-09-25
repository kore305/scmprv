from django.shortcuts import render
from .forms import LinkCheckForm
from .utils import check_url_with_google_safe_browsing, extract_domain
from whatsapp_verifier.models import FederalProgram
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
