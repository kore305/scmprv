from django.shortcuts import render

# Create your views here.

def landing_page(request):
    return render(request, "website/landing.html")

def verify_link(request):
    return render(request, "website/verify_link.html")

def report_scam(request):
    return render(request, "website/report_scam.html")

def initiatives(request):
    return render(request, "website/initiatives.html")

def resources(request):
    return render(request, "website/resources.html")
