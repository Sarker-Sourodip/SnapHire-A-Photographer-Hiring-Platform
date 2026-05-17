from django.urls import path
from . import views

urlpatterns = [

    path(
        '',
        views.home,
        name='feature_home'
    ),

    path(
        'notifications/',
        views.notifications,
        name='notifications'
        
    ),
    path('faq/', views.faq, name='faq'),

]