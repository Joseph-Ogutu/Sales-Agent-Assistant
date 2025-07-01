from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Lead, Interaction
from .tasks import start_sequence
from .forms import RegisterForm, LoginForm, LeadForm
import json
from collections import Counter

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully. Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    lead_form = LeadForm()
    filter_type = request.GET.get('filter_type', '')
    filter_value = request.GET.get('filter_value', '')

    leads = Lead.objects.all()
    interactions = Interaction.objects.all()
    
    if filter_type == 'score':
        leads = leads.filter(score__gte=float(filter_value)) if filter_value else leads
    elif filter_type == 'industry':
        leads = leads.filter(industry__iexact=filter_value) if filter_value else leads
    elif filter_type == 'engagement':
        leads = leads.filter(behavioral_profile__contains=f'"engagement_level": {float(filter_value)}') if filter_value else leads

    total_leads = leads.count()
    active_sequences = Interaction.objects.filter(is_reply=False).values('lead').distinct().count()

    engagement_levels = []
    for lead in leads:
        try:
            engagement_levels.append(json.loads(lead.behavioral_profile).get('engagement_level', 0))
        except json.JSONDecodeError:
            engagement_levels.append(0)

    if request.method == 'POST':
        lead_form = LeadForm(request.POST)
        if lead_form.is_valid():
            lead = lead_form.save(commit=False)
            lead.behavioral_profile = '{"engagement_level": 0}'
            lead.pain_points = json.dumps(lead_form.cleaned_data['pain_points'].split(', ')) if lead_form.cleaned_data['pain_points'] else '[]'
            lead.save()
            messages.success(request, f'Lead {lead.name} created successfully.')
            return redirect('dashboard')

    return render(request, 'dashboard.html', {
        'leads': leads,
        'interactions': interactions,
        'user': request.user,
        'lead_form': lead_form,
        'total_leads': total_leads,
        'active_sequences': active_sequences,
        'filter_type': filter_type,
        'filter_value': filter_value,
        'engagement_levels': engagement_levels
    })

@login_required
def analytics_dashboard(request):
    leads = Lead.objects.all()
    total_leads = leads.count()
    engaged_leads = leads.filter(score__gt=0.5).count()
    converted_leads = leads.filter(score__gt=0.7).count()
    conversion_rate = (converted_leads / total_leads * 100) if total_leads else 0
    
    engagement_scores = [json.loads(lead.behavioral_profile).get('engagement_level', 0) for lead in leads]
    avg_engagement = sum(engagement_scores) / len(engagement_scores) if engagement_scores else 0
    interactions = Interaction.objects.filter(is_reply=False)
    sequence_completion = (interactions.count() / (total_leads * 5) * 100) if total_leads else 0
    
    # Lead distribution by industry
    industry_counts = Counter(lead.industry for lead in leads)
    industry_data = [{'industry': industry, 'count': count} for industry, count in industry_counts.items()]
    
    return render(request, 'analytics.html', {
        'leads': leads,
        'conversion_rate': conversion_rate,
        'avg_engagement': avg_engagement * 100,
        'sequence_completion': sequence_completion,
        'funnel_data': [total_leads, engaged_leads, converted_leads],
        'industry_data': industry_data
    })

@login_required
def start_sequence_view(request, lead_id):
    start_sequence(lead_id)
    leads = Lead.objects.all()
    total_leads = leads.count()
    active_sequences = Interaction.objects.filter(is_reply=False).values('lead').distinct().count()
    return render(request, 'dashboard.html', {
        'leads': leads,
        'interactions': Interaction.objects.all(),
        'message': f"Sequence started for lead {lead_id}",
        'user': request.user,
        'lead_form': LeadForm(),
        'total_leads': total_leads,
        'active_sequences': active_sequences
    })