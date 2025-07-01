import requests
from transformers import pipeline
from openai import OpenAI
from sklearn.linear_model import LogisticRegression
import json
from twilio.rest import Client

openai_client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
twilio_client = Client("TWILIO_ACCOUNT_SID", "TWILIO_AUTH_TOKEN")

def enrich_lead(email):
    try:
        response = requests.get(
            f"https://person.clearbit.com/v2/combined/find?email={email}",
            headers={"Authorization": "Bearer YOUR_CLEARBIT_API_KEY"}
        )
        return response.json() if response.status_code == 200 else {}
    except:
        return {}

def profile_behavior(interactions, lead_data):
    classifier = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    sentiments = [classifier(i.content)[0] for i in interactions]
    engagement = sum(1 for s in sentiments if s["label"] == "POSITIVE") / len(sentiments) if sentiments else 0
    pain_points = extract_pain_points(lead_data, interactions)
    return json.dumps({"engagement_level": engagement, "pain_points": pain_points})

def extract_pain_points(lead_data, interactions):
    return ["slow sales cycle", "high churn"]

def generate_pain_based_message(lead, pain_points, channel="email"):
    prompt = f"""
    Write a concise, professional, pain-based {'email' if channel == 'email' else 'WhatsApp/LinkedIn message'} for {lead.name} at {lead.company}.
    Address pain points: {', '.join(pain_points)}.
    Use an empathetic, conversational tone. Keep it under {'150 words' if channel == 'email' else '50 words'}.
    """
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200 if channel == "email" else 100
    )
    return response.choices[0].message.content

def generate_coaching_prompt(interaction_content):
    prompt = f"Analyze this sales interaction: {interaction_content}. Suggest 3 specific improvements for the rep, focusing on objection handling and tone."
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )
    return response.choices[0].message.content

def score_lead(lead_id):
    from .models import Lead, Interaction
    lead = Lead.objects.get(id=lead_id)
    interactions = Interaction.objects.filter(lead=lead)
    profile = json.loads(lead.behavioral_profile) if lead.behavioral_profile else {}
    features = [
        profile.get('engagement_level', 0),
        1 if lead.company_size > 100 else 0,
        1 if lead.industry == 'Tech' else 0
    ]
    model = LogisticRegression().fit([[0, 0, 0], [1, 1, 1]], [0, 1])
    score = model.predict_proba([features])[0][1]
    lead.score = score
    lead.save()
    return score

def send_whatsapp(to, content):
    message = twilio_client.messages.create(
        from_='whatsapp:+14155238886',
        body=content,
        to=f'whatsapp:{to}'
    )
    return message.sid

def sync_with_crm(lead_id):
    from .models import Lead, CRMIntegration
    lead = Lead.objects.get(id=lead_id)
    try:
        response = requests.post(
            "https://api.hubapi.com/crm/v3/objects/contacts",
            json={"properties": {"email": lead.email, "company": lead.company, "phone": lead.phone}},
            headers={"Authorization": "Bearer YOUR_HUBSPOT_API_KEY"}
        )
        if response.status_code == 201:
            CRMIntegration.objects.create(lead=lead, crm_id=response.json()['id'], sync_status='success')
    except:
        CRMIntegration.objects.create(lead=lead, crm_id='failed', sync_status='failed')