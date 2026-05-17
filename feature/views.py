from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Notification
from .models import FAQ

@login_required
def home(request):

    return render(
        request,
        'feature/home.html'
    )


@login_required
def notifications(request):

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(
        request,
        'feature/notifications.html',
        {
            'notifications': notifications
        }
    )

def faq(request):

    faqs = FAQ.objects.all()

    return render(request, 'feature/faq.html', {
        'faqs': faqs
    })