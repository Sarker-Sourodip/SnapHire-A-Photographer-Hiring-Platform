from django.shortcuts import render
from django.views.decorators.cache import never_cache

# Create your views here.

@never_cache
def home(request):
    return render(request, 'core/home.html')

@never_cache
def about(request):
    return render(request, 'core/about.html')

@never_cache
def contact(request):
    return render(request, 'core/contact.html')