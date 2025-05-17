from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import re
from decouple import config


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirm Password"
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

class LoginForm(forms.Form):
    username = forms.CharField(max_length=config("USERNAME_MAX_LENGTHT"), required=True)
    password = forms.CharField(max_length=config("PASSWORD_MAX_LENGTHT"), required=True, widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data['username']
        if not re.match(r'^[\w]+$', username):
            raise ValidationError("Login need to involve only letters, digits and underscores.")
        return username

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=config("USERNAME_MAX_LENGTHT"), required=True)
    email = forms.EmailField(required=True)
    password = forms.CharField(max_length=config("PASSWORD_MAX_LENGTHT"), required=True, widget=forms.PasswordInput)

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
        if len(email) > 50:
            raise ValidationError("Email is too long.")
        return email

class EmailVerificationForm(forms.Form):
    code = forms.CharField(max_length=6, min_length=6, required=True)

    def clean_code(self):
        code = self.cleaned_data['code']
        if not code.isdigit():
            raise ValidationError("Code need to be only digits")
        return code
    
class RecoveryForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email, is_active=True).exists():
            raise ValidationError("This email is not registered.")
        return email
    
class PasswordForm(forms.Form):
    password = forms.CharField(max_length=config("PASSWORD_MAX_LENGTHT"), required=True, widget=forms.PasswordInput)
    password2 = forms.CharField(max_length=config("PASSWORD_MAX_LENGTHT"), required=True, widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")

        if password != password2:
            raise ValidationError("Passwords do not match.")
        return cleaned_data