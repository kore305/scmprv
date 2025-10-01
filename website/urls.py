from django.urls import path
from . import views

urlpatterns = [
    path("", views.landing_page, name="landing"),
    path("verify-link/", views.verify_link, name="verify_link"),
    path("report-scam/", views.report_scam, name="report_scam"),
    path('thank-you/', views.thank_you, name='thank_you'),
    path("initiatives/", views.initiatives, name="initiatives"),
    path("resources/", views.resources, name="resources"),
    path("chatbot/", views.chatbot, name="chatbot"),
    path("api/report-scam/", views.api_report_scam, name="api_report_scam"),
    
]
