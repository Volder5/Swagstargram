from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import random
from django.core.mail import send_mail
from django.views.decorators.http import require_http_methods
from .forms import *


@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.user.is_authenticated:
        return redirect('main')
    print(request.method)
    form = LoginForm(request.POST)
    if form.is_valid():     
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, "Invalid credentials")
    else:
        messages.error(request, "Please fix the errors in the form")
    return render(request, "users/login.html")


@require_http_methods(["GET", "POST"])
def register_page(request):
    print(request.method)
    form = RegisterForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered")
        else:
            verification_code = str(random.randint(100000, 999999))
            request.session['registration_data'] = {
                'username': username,
                'email': email,
                'password': password,
                'code': verification_code
            }

            send_mail(
                'Verify your email',
                f'Your verification code is {verification_code}',
                'noreply@swagstargram.com',
                [email],
                fail_silently=False,
            )

            return redirect('email_verify')
    else:
        messages.error(request, "Please fix the errors in the form")
    return render(request, "users/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def email_verification_page(request):
    print(request.method)
    form = EmailVerificationForm(request.POST)
    reg_data = request.session.get('registration_data', {})
    if form.is_valid():
        input_code = form.cleaned_data['code']
        if input_code == reg_data.get('code'):
            User.objects.create_user(
                username=reg_data['username'],
                email=reg_data['email'],
                password=reg_data['password']
            )
            messages.success(request, "Email verified and account created!")
            return redirect('login')
        else:
            messages.error(request, "Invalid verification code")
    else:
        messages.error(request, "Please fix the errors in the form")
    return render(request, "users/email_verification.html", {"form": form})

@login_required
def profile_page(request):
    return render(request, "users/profile.html")