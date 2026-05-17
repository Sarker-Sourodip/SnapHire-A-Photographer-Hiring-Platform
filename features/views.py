from django.shortcuts import render
<<<<<<< HEAD
from .models import FAQ


def faq_page(request):
    faqs = FAQ.objects.all()

    return render(request, 'features/faq.html', {
        'faqs': faqs
    })
=======

def faq(request):
    return render(request, 'features/faq.html')
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
