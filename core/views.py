from django.shortcuts import render

from django.http import HttpResponse


def home(request):
    return HttpResponse("Taxi Booking System is running!")

def admin_login(request):
    return render(request, 'admin_login.html')