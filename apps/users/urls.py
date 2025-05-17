from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login_page, name='login'),
    path("register/", views.register_page,  name='register'),
    path("profile/", views.profile_page,  name='profile'),
    path('verify-email/<int:recovery>/', views.email_verification_page, name='email_verify'),
    path('recovery/', views.recovery_page, name='recovery'),
    path('change_password/', views.recovery_page, name='change_password'),
    path('users/change-password/', views.change_password_page, name='change_password'),
]