from django.shortcuts import render
<<<<<<< HEAD
from django.views.decorators.cache import never_cache

# Create your views here.

@never_cache
def home(request):
    return render(request, 'core/home.html')

@never_cache
def about(request):
    return render(request, 'core/about.html')

@never_cache
=======
from django.views.decorators.cache import never_cache  # <-- NEW: Imported never_cache

# Create your views here.

@never_cache  # <-- NEW: Forces the browser to reload the navbar correctly
def home(request):
    return render(request, 'core/home.html')

@never_cache  # <-- NEW
def about(request):
    return render(request, 'core/about.html')

@never_cache  # <-- NEW
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
def contact(request):
    return render(request, 'core/contact.html')