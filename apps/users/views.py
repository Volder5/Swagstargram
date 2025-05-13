from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required


def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, "users/login.html")

import random
from django.core.mail import send_mail

def register_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

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

    return render(request, "users/register.html")

def email_verification_page(request):
    if request.method == "POST":
        input_code = request.POST.get('code')
        reg_data = request.session.get('registration_data', {})

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

    return render(request, "users/email_verification.html")

@login_required
def profile_page(request):
    return render(request, "users/profile.html")