from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('faq/', views.faq_page, name='faq'),
=======
    path('faq/', views.faq, name='faq'),
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
]