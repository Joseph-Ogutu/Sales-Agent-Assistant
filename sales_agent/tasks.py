import threading
import time
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from .models import Lead, Interaction
from .utils import enrich_lead, profile_behavior, generate_pain_based_message, generate_coaching_prompt, score_lead, send_whatsapp, sync_with_crm
import base64
from email.mime.text import MIMEText

def send_email(to, subject, content):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.send'])
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(content)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId='me', body={'raw': raw}).execute()

def check_reply(email, thread_id):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.readonly'])
    service = build('gmail', 'v1', credentials=creds)
    results = service.users().messages().list(userId='me', q=f"from:{email}").execute()
    messages = results.get('messages', [])
    return any(msg['threadId'] == thread_id for msg in messages)

def handle_reply(lead_id, reply_content):
    lead = Lead.objects.get(id=lead_id)
    classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
    sentiment = classifier(reply_content)[0]
    
    interaction = Interaction.objects.create(
        lead=lead,
        message_type="email",
        content=reply_content,
        is_reply=True,
        thread_id=f"thread_{lead.id}",
        coaching_feedback=generate_coaching_prompt(reply_content)
    )
    
    if sentiment["label"] == "POSITIVE":
        response = generate_pain_based_message(lead, lead.get_pain_points(), channel="email")
        send_email(lead.email, "Re: Our Previous Conversation", response)
        Interaction.objects.create(
            lead=lead,
            message_type="email",
            content=response,
            thread_id=f"thread_{lead.id}"
        )
    else:
        notify_rep(lead_id, reply_content)

def notify_rep(lead_id, reply_content):
    pass

def execute_sequence(lead_id):
    lead = Lead.objects.get(id=lead_id)
    interactions = Interaction.objects.filter(lead=lead)
    lead_data = enrich_lead(lead.email)
    lead.behavioral_profile = profile_behavior(interactions, lead_data)
    lead.pain_points = json.dumps(extract_pain_points(lead_data, interactions))
    score_lead(lead_id)
    sync_with_crm(lead_id)
    lead.save()
    
    channels = ["email", "whatsapp", "email", "linkedin", "email"]
    for touch, channel in enumerate(channels):
        if check_reply(lead.email, f"thread_{lead.id}"):
            break
        content = generate_pain_based_message(lead, lead.get_pain_points(), channel)
        if channel == "email":
            send_email(lead.email, f"Solving {lead.company} Challenges", content)
        elif channel == "whatsapp" and lead.phone:
            send_whatsapp(lead.phone, content)
        elif channel == "linkedin":
            Interaction.objects.create(
                lead=lead,
                message_type="linkedin",
                content=content,
                thread_id=f"thread_{lead.id}"
            )
            continue
        Interaction.objects.create(
            lead=lead,
            message_type=channel,
            content=content,
            thread_id=f"thread_{lead.id}"
        )
        time.sleep(2 * 24 * 60 * 60)

def start_sequence(lead_id):
    thread = threading.Thread(target=execute_sequence, args=(lead_id,))
    thread.start()