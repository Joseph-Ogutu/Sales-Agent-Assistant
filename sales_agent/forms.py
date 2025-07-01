from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Lead

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Enter a valid email address.")
    company = forms.CharField(max_length=100, required=True, help_text="Enter your company name.")

    class Meta:
        model = User
        fields = ["username", "email", "company", "password1", "password2"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Optionally store company in a user profile model (not implemented here)
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'email', 'phone', 'company', 'industry', 'pain_points']
        widgets = {
            'pain_points': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter pain points (e.g., slow sales cycle, high churn)'})
        }