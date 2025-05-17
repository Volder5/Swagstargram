from django.urls import path
from . import views

urlpatterns = [
    path("", views.main_page, name='main'),
    path("test/", views.messages_test,  name='test')
]