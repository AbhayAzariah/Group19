from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, 'base/home.html')

def room(request):
    return render(request, 'base/room.html')

def find(request):
    return render(request, 'base/find.html')

def compare(request):
    return render(request, 'base/compare.html')

def register(request):
    return render(request, 'base/register.html')