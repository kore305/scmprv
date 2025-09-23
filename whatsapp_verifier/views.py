from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from twilio.rest import Client
from decouple import config
from .models import WhatsAppSession
from .utils import verify_link_virustotal, get_program_info, translate_text

# Twilio configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = config('TWILIO_WHATSAPP_NUMBER')

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp_message(to_number, message):
    """Send a message via WhatsApp using Twilio"""
    try:
        message = twilio_client.messages.create(
            body=message,
            from_=f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            to=f'whatsapp:{to_number}'
        )
        return message.sid
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")
        return None

def get_main_menu_message(language='en'):
    messages = {
        'en': "Welcome to Federal Programs Info Service. Please choose an option:\n1. Verify link\n2. Get information\n3. Change language",
        'igbo': "Nnọọ na Federal Programs Info Service. Biko họrọ nhọrọ:\n1. Nyochaa njikọ\n2. Nweta ozi\n3. Gbanwee asụsụ",
        'hausa': "Barka da zuwa Federal Programs Info Service. Da fatan za a zaɓi zaɓi:\n1. Tabbatar da hanyar haɗi\n2. Sami bayani\n3. Canza harshe",
        'yoruba': "Kaabo si Federal Programs Info Service. Jọwọ yan aṣayan:\n1. Ṣayẹwo ọna asopọ\n2. Gba alaye\n3. Yi ede pada"
    }
    return messages.get(language, messages['en'])

def get_prompt_message(prompt, language='en'):
    translations = {
        'en': prompt,
        'igbo': translate_text(prompt, 'ig'),
        'hausa': translate_text(prompt, 'ha'),
        'yoruba': translate_text(prompt, 'yo')
    }
    return translations.get(language, prompt)

def get_language_options_message():
    return "Please choose your language:\n1. English\n2. Igbo\n3. Hausa\n4. Yoruba"

@csrf_exempt
@require_POST
def whatsapp_webhook(request):
    """Handle incoming WhatsApp messages from Twilio"""
    try:
        # Extract incoming message data from Twilio
        data = request.POST
        from_number = data.get('From', '').replace('whatsapp:', '')
        message_body = data.get('Body', '').strip().lower()
        
        # Get or create user session
        session, created = WhatsAppSession.objects.get_or_create(phone_number=from_number)
        
        # Handle language selection
        if message_body in ['english', 'igbo', 'hausa', 'yoruba']:
            session.language = message_body
            session.current_step = 'main_menu'
            session.save()
            send_whatsapp_message(from_number, get_main_menu_message(session.language))
            return HttpResponse("OK")
        
        # Handle main menu options
        if session.current_step == 'main_menu':
            if message_body == 'verify link':
                session.current_step = 'awaiting_link'
                session.save()
                prompt = get_prompt_message("Please paste the link you want to verify:", session.language)
                send_whatsapp_message(from_number, prompt)
            elif message_body == 'get information':
                session.current_step = 'awaiting_program_name'
                session.save()
                prompt = get_prompt_message("Please enter the name of the federal program:", session.language)
                send_whatsapp_message(from_number, prompt)
            elif message_body == 'change language':
                session.current_step = 'awaiting_language'
                session.save()
                send_whatsapp_message(from_number, get_language_options_message())
            else:
                send_whatsapp_message(from_number, get_main_menu_message(session.language))
        
        # Handle link verification
        elif session.current_step == 'awaiting_link':
            result = verify_link_virustotal(message_body)
            if session.language != 'en':
                result = translate_text(result, session.language)
            send_whatsapp_message(from_number, result)
            session.current_step = 'main_menu'
            session.save()
            send_whatsapp_message(from_number, get_main_menu_message(session.language))
        
        # Handle program information request
        elif session.current_step == 'awaiting_program_name':
            result = get_program_info(message_body, session.language)
            send_whatsapp_message(from_number, result)
            session.current_step = 'main_menu'
            session.save()
            send_whatsapp_message(from_number, get_main_menu_message(session.language))
        
        # Handle language change
        elif session.current_step == 'awaiting_language':
            if message_body in ['english', 'igbo', 'hausa', 'yoruba']:
                session.language = message_body
                session.current_step = 'main_menu'
                session.save()
                send_whatsapp_message(from_number, get_main_menu_message(session.language))
            else:
                send_whatsapp_message(from_number, get_language_options_message())
        
        return HttpResponse("OK")
    
    except Exception as e:
        print(f"Error processing WhatsApp message: {e}")
        return HttpResponse("Error", status=500)