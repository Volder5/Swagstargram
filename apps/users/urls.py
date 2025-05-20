from django.urls import path, re_path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("login/", views.login_page, name='login'),
    path('logout/', views.logout_page, name='logout'),
    path("register/", views.register_page,  name='register'),
    re_path(r'^profile/(?P<username>\w+)?/$', views.profile_page, name='profile'),
    re_path(r'^verify-email/(?P<recovery>\d+)?/$', views.email_verification_page, name='email_verify'),
    path('recovery/', views.recovery_page, name='recovery'),
    path('change-password/', views.change_password_page, name='change_password'),
]