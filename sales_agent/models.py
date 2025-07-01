from django.db import models
import json

class Lead(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100)
    industry = models.CharField(max_length=100)
    pain_points = models.TextField(blank=True)
    behavioral_profile = models.TextField(blank=True)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_pain_points(self):
        return json.loads(self.pain_points) if self.pain_points else []

class CRMIntegration(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    crm_id = models.CharField(max_length=100)
    last_synced = models.DateTimeField(auto_now=True)
    sync_status = models.CharField(max_length=50, default='pending')

class Interaction(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE)
    message_type = models.CharField(max_length=50)
    content = models.TextField()
    coaching_feedback = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_reply = models.BooleanField(default=False)
    thread_id = models.CharField(max_length=100)