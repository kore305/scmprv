from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
import requests
import time
import threading
from .models import WhatsAppSession
from .utils import verify_link_virustotal, get_program_info, translate_text

# Twilio configuration
TWILIO_ACCOUNT_SID = config('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = config('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = config('TWILIO_WHATSAPP_NUMBER')

def send_whatsapp_message(to_number, message):
    """Send message using Twilio API directly"""
    try:
        url = f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json"
        
        auth = (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        data = {
            'From': f'whatsapp:{TWILIO_WHATSAPP_NUMBER}',
            'To': f'whatsapp:{to_number}',
            'Body': message
        }
        
        response = requests.post(url, auth=auth, data=data)
        
        if response.status_code == 201:
            print("Message sent successfully")
            return True
        else:
            print(f"Twilio API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending message: {e}")
        return False

def get_main_menu_message():
    """Simple menu without translation for now"""
    return """Welcome to Federal Programs Info Service! 📊

What would you like to do?
1. 🔗 Verify a link
2. ℹ️ Get program information  
3. 🌐 Change language

Reply with 1, 2, or 3"""

def send_menu_after_delay(phone_number, delay=5):
    """Send menu after a delay"""
    def delayed_menu():
        time.sleep(delay)
        send_whatsapp_message(phone_number, get_main_menu_message())
    
    # Run in background thread to avoid blocking
    thread = threading.Thread(target=delayed_menu)
    thread.daemon = True
    thread.start()

@csrf_exempt
def whatsapp_webhook(request):
    """Handle incoming WhatsApp messages"""
    
    # Handle GET request (Twilio webhook verification)
    if request.method == 'GET':
        print("GET request - Webhook verification")
        return HttpResponse("Webhook verified!")
    
    # Handle POST request (messages)
    elif request.method == 'POST':
        print("POST request - Message received")
        
        try:
            data = request.POST
            from_number = data.get('From', '').replace('whatsapp:', '')
            message_body = data.get('Body', '').strip().lower()
            
            print(f"Message from {from_number}: {message_body}")
            
            # Get or create session
            session, created = WhatsAppSession.objects.get_or_create(phone_number=from_number)
            
            # Handle language selection
            if message_body in ['english', 'igbo', 'hausa', 'yoruba', 'en', 'ig', 'ha', 'yo']:
                lang_map = {'english': 'en', 'igbo': 'ig', 'hausa': 'ha', 'yoruba': 'yo', 
                           'en': 'en', 'ig': 'ig', 'ha': 'ha', 'yo': 'yo'}
                session.language = lang_map[message_body]
                session.current_step = 'main_menu'
                session.save()
                send_whatsapp_message(from_number, f"Language set to {message_body.capitalize()}! 🌍")
                # Don't send menu immediately after language change
                send_menu_after_delay(from_number, 2)
                return HttpResponse("OK")
            
            # Handle main menu options
            if session.current_step == 'main_menu':
                if message_body in ['1', 'verify', 'verify link', 'link']:
                    session.current_step = 'awaiting_link'
                    session.save()
                    send_whatsapp_message(from_number, "🔗 Please paste the link you want to verify:\n\nExample: https://google.com")
                    
                elif message_body in ['2', 'info', 'information', 'program']:
                    session.current_step = 'awaiting_program'
                    session.save()
                    send_whatsapp_message(from_number, "ℹ️ Please enter the program name:\n\nExamples:\n- N-Power\n- Anchor Borrowers\n- Conditional Cash Transfer")
                    
                elif message_body in ['3', 'language', 'change language']:
                    session.current_step = 'awaiting_language'
                    session.save()
                    send_whatsapp_message(from_number, "🌐 Choose your language:\n\n1. English\n2. Igbo\n3. Hausa\n4. Yoruba")
                    
                else:
                    # Show main menu for any other message
                    send_whatsapp_message(from_number, get_main_menu_message())
            
            # Handle link verification
            elif session.current_step == 'awaiting_link':
                # Send immediate acknowledgment
                send_whatsapp_message(from_number, "⏳ Analyzing your link... Please wait a moment.")
                
                # Process the link analysis
                result = verify_link_virustotal(message_body)
                
                # Send the result
                send_whatsapp_message(from_number, result)
                
                # Return to main menu
                session.current_step = 'main_menu'
                session.save()
                
                # Send menu after delay
                send_menu_after_delay(from_number, 5)
                
            # Handle program information request
            elif session.current_step == 'awaiting_program':
                result = get_program_info(message_body, session.language)
                send_whatsapp_message(from_number, result)
                
                # Return to main menu
                session.current_step = 'main_menu'
                session.save()
                
                # Send menu after delay
                send_menu_after_delay(from_number, 3)
                
            # Handle language change
            elif session.current_step == 'awaiting_language':
                lang_options = {'1': 'en', '2': 'ig', '3': 'ha', '4': 'yo'}
                if message_body in lang_options:
                    session.language = lang_options[message_body]
                    session.current_step = 'main_menu'
                    session.save()
                    lang_names = {'en': 'English', 'ig': 'Igbo', 'ha': 'Hausa', 'yo': 'Yoruba'}
                    send_whatsapp_message(from_number, f"✅ Language set to {lang_names[session.language]}!")
                    send_menu_after_delay(from_number, 2)
                else:
                    send_whatsapp_message(from_number, "❌ Invalid choice. Please select 1, 2, 3, or 4")
                    send_whatsapp_message(from_number, "🌐 Choose your language:\n1. English\n2. Igbo\n3. Hausa\n4. Yoruba")
            
            return HttpResponse("OK")
            
        except Exception as e:
            print(f"Error: {e}")
            # Reset session on error
            try:
                session.current_step = 'main_menu'
                session.save()
                send_whatsapp_message(from_number, "❌ An error occurred. Returning to main menu.")
                send_menu_after_delay(from_number, 3)
            except:
                pass
            return HttpResponse("Error", status=500)
    
    return HttpResponse("Method not allowed", status=405)