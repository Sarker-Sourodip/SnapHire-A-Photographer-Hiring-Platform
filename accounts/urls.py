from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('photographer/setup/', views.photographer_setup, name='photographer_setup'),
    path('photographer/dashboard/', views.photographer_dashboard, name='photographer_dashboard'),
    path('photographer/portfolio/', views.portfolio_list, name='portfolio_list'),
    path('photographer/portfolio/add/', views.portfolio_create, name='portfolio_create'),
    path('photographer/portfolio/<int:pk>/edit/', views.portfolio_edit, name='portfolio_edit'),
    path('photographer/portfolio/<int:pk>/delete/', views.portfolio_delete, name='portfolio_delete'),
    path('photographers/', views.photographers_list, name='photographers_list'),
    path('photographers/<int:pk>/', views.photographer_public, name='photographer_public'),
    path('developer/dashboard/', views.developer_dashboard, name='developer_dashboard'),
    path('developer/user/<int:user_pk>/delete/', views.developer_delete_user, name='developer_delete_user'),
    path('client/dashboard/', views.client_dashboard, name='client_dashboard'),
    path('booking/<int:booking_pk>/review/', views.add_review, name='add_review'),
]