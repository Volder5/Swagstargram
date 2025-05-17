from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re

class LoginForm(forms.Form):
    username = forms.CharField(max_length=16, required=True)
    password = forms.CharField(max_length=24, required=True, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[\w]+$', username):
            raise ValidationError("Login need to involve only letters, digits and underscores.")
        return username

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=16, required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(max_length=24, required=True, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[\w]+$', username):
            raise ValidationError("Login need to involve only letters, digits and underscores.")
        if User.objects.filter(username=username, is_active=True).exists():
            raise ValidationError("Login is used by another user.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("This email is already registered.")
        if len(email) > 32:
            raise ValidationError("Email is too long.")
        return email

class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, required=True)

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise ValidationError("Code need to be only digits")
        return code