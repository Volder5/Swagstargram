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
from .models import EmailVerification
from django.utils import timezone
from datetime import timedelta


@require_http_methods(["GET", "POST"])
def login_page(request):
    if request.user.is_authenticated:
        return redirect('main')
    form = LoginForm(request.POST)
    if request.method == "POST" and form.is_valid():
        print(request.method)
        username = form.cleaned_data["username"]
        password = form.cleaned_data["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main')
        else:
            messages.error(request, "Invalid credentials")
    elif request.method == "POST":
        messages.error(request, "Please fix the errors in the form")
    return render(request, "users/login.html")


@require_http_methods(["GET", "POST"])
def register_page(request):
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        verification_code = str(random.randint(100000, 999999))

        # Check for inactive user
        try:
            user = User.objects.get(username=username, is_active=False)
            # Update email and password if changed
            user.email = email
            user.set_password(password)
            user.save()
            # Update or create verification record
            verification = EmailVerification.objects.filter(
                user=user, is_verified=False).first()
            if verification:
                verification.code = verification_code
                verification.created_at = timezone.now()  # Reset timestamp
                verification.save()
            else:
                EmailVerification.objects.create(
                    user=user, code=verification_code)
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False
            )
            EmailVerification.objects.create(user=user, code=verification_code)

        # Set session
        request.session['user_id'] = user.id

        # Send email
        try:
            send_mail(
                'Verify your email',
                f'Your verification code is {verification_code}',
                'noreply@swagstargram.com',
                [email],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(request, f"Failed to send email: {str(e)}")
            user.delete()  # Roll back user creation
            return render(request, "users/register.html", {"form": form})

        messages.success(request, "Verification code sent to your email.")
        return redirect('email_verify')
    elif request.method == "POST":
        messages.error(request, "Please fix the errors in the form.")

    return render(request, "users/register.html", {"form": form})


@require_http_methods(["GET", "POST"])
def email_verification_page(request, recovery=False):
    form = EmailVerificationForm(request.POST)
    if request.method == "POST" and form.is_valid():
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Session expired. Please register again.")
            return redirect('register')
        try:
            user = User.objects.get(id=user_id)
            input_code = form.cleaned_data['code']
            verification = EmailVerification.objects.filter(
                user=user,
                code=input_code,
                is_verified=False,  # Always check unverified codes
                created_at__gte=timezone.now() - timedelta(minutes=5)
            ).first()
            if verification:
                if not recovery:
                    verification.is_verified = True
                    verification.save()
                    user.is_active = True
                    user.save()
                    messages.success(
                        request, "Email verified and account created!")
                    if 'user_id' in request.session:
                        del request.session['user_id']
                    if user is not None:
                        login(request, user)
                        return redirect('main')
                    else:
                        return redirect('login')
                else:
                    verification.is_verified = True
                    verification.save()
                    return redirect("change_password")
            else:
                messages.error(
                    request, "Invalid or expired verification code.")
        except User.DoesNotExist:
            messages.error(request, "Invalid session. Please register again.")
            return redirect('register')
    elif request.method == "POST":
        messages.error(request, "Please fix the errors in the form.")

    return render(request, "users/email_verification.html", {"form": form, "recovery": recovery})


@require_http_methods(["GET", "POST"])
def recovery_page(request):
    form = RecoveryForm(request.POST)
    if request.method == "POST" and form.is_valid():
        email = form.cleaned_data['email']
        user = User.objects.filter(email=email, is_active=True).first()
        if user:
            verification_code = str(random.randint(100000, 999999))
            EmailVerification.objects.create(
                user=user,
                code=verification_code,
                is_verified=False
            )
            try:
                send_mail(
                    'Verify your email',
                    f'Your verification code is {verification_code}\nUsername: {user.username}',
                    'noreply@swagstargram.com',
                    [email],
                    fail_silently=False,
                )
            except Exception as e:
                messages.error(request, f"Failed to send email: {str(e)}")
                return render(request, "users/recovery_email_input.html", {"form": form})
            messages.success(request, "Recovery code sent to your email.")
            request.session['user_id'] = user.id
            return redirect('email_verify', recovery=1)
        else:
            messages.error(request, "No active user found with this email.")
    elif request.method == "POST":
        messages.error(request, "Please fix the errors in the form.")

    return render(request, "users/recovery_email_input.html", {"form": form})


@require_http_methods(["GET", "POST"])
def change_password_page(request):
    form = ChangePasswordForm(request.POST)
    if request.method == "POST" and form.is_valid():
        user_id = request.session.get('user_id')
        if not user_id:
            messages.error(request, "Session expired. Please try again.")
            return redirect('recovery')
        try:
            user = User.objects.get(id=user_id)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, "Password changed successfully!")
            if 'user_id' in request.session:
                del request.session['user_id']
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "Invalid session. Please try again.")
            return redirect('recovery')

    elif request.method == "POST":
        messages.error(request, "Please fix the errors in the form.")

    return render(request, "users/change_password.html", {"form": form})


@login_required
def profile_page(request):
    return render(request, "users/profile.html")
