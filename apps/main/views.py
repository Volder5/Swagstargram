from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required


@login_required
def main_page(request):
    return render(request, "main/index.html")

@login_required
def messages_test(request):
    return render(request, "main/messages_test.html")

