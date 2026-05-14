from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Avg, Count
from functools import wraps

from .forms import RegistrationForm, LoginForm, PhotographerForm, PortfolioForm, ReviewForm, BookingForm
from .models import Photographer, Profile, Portfolio, Booking, Review

# --- NEW: Import the Service ---
from .services import create_user_safely

def redirect_to_dashboard(request):
    """
    Helper function to redirect users to their correct dashboard 
    based on their session role.
    """
    role = request.session.get('role')
    if role == 'client':
        return redirect('photographers_list')
    elif role == 'photographer':
        return redirect('photographer_dashboard')
    elif role == 'developer':
        return redirect('developer_dashboard')
    return redirect('home')


@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # Use the Single Channel
            user, created = create_user_safely(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                role=form.cleaned_data['role']
            )

            if not created:
                messages.error(request, 'Username already taken.')
                return render(request, 'accounts/register.html', {'form': form})

            # Success path
            login(request, user)
            request.session['role'] = user.profile.role
            messages.success(request, 'Registration successful!')
            
            if request.session['role'] == 'photographer':
                return redirect('photographer_setup')
            return redirect_to_dashboard(request)
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


@never_cache
def login_view(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)

    if request.method == 'POST':
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful.')
            
            # Save role to session
            try:
                request.session['role'] = user.profile.role
            except Exception:
                request.session['role'] = 'guest'

            return redirect_to_dashboard(request)
    else:
        form = LoginForm(request=request)

    return render(request, 'accounts/login.html', {'form': form})


@never_cache
def logout_view(request):
    list(messages.get_messages(request))
    logout(request)
    return redirect('login')


@login_required
@never_cache
def photographer_setup(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer, created = Photographer.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = PhotographerForm(request.POST, instance=photographer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Photographer profile saved.')
            return redirect('home')
    else:
        form = PhotographerForm(instance=photographer)

    return render(request, 'accounts/photographer_setup.html', {'form': form})


@login_required
@never_cache
def photographer_dashboard(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer, created = Photographer.objects.get_or_create(user=request.user)
    portfolios = Portfolio.objects.filter(photographer=photographer)
    return render(request, 'accounts/photographer_dashboard.html', {
        'photographer': photographer,
        'portfolios': portfolios,
    })


@login_required
@never_cache
def portfolio_list(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer = Photographer.objects.get(user=request.user)
    items = Portfolio.objects.filter(photographer=photographer)
    return render(request, 'accounts/portfolio_list.html', {'items': items})


@login_required
@never_cache
def portfolio_create(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer = Photographer.objects.get(user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES)
        if form.is_valid():
            p = form.save(commit=False)
            p.photographer = photographer
            p.save()
            messages.success(request, 'Portfolio item added.')
            return redirect('photographer_dashboard')
    else:
        form = PortfolioForm()
    return render(request, 'accounts/portfolio_form.html', {'form': form})


@login_required
@never_cache
def portfolio_edit(request, pk):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer = Photographer.objects.get(user=request.user)
    item = Portfolio.objects.filter(photographer=photographer, pk=pk).first()
    if not item:
        return redirect('photographer_dashboard')
    if request.method == 'POST':
        form = PortfolioForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio item updated.')
            return redirect('photographer_dashboard')
    else:
        form = PortfolioForm(instance=item)
    return render(request, 'accounts/portfolio_form.html', {'form': form, 'item': item})


@login_required
@never_cache
def portfolio_delete(request, pk):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer = Photographer.objects.get(user=request.user)
    item = Portfolio.objects.filter(photographer=photographer, pk=pk).first()
    if not item:
        return redirect('photographer_dashboard')
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Portfolio item deleted.')
        return redirect('photographer_dashboard')
    return render(request, 'accounts/confirm_delete.html', {'object': item})


def photographers_list(request):
    photographers = (
        Photographer.objects.select_related('user').filter(user__profile__role='photographer').prefetch_related('portfolio_set').annotate(portfolio_count=Count('portfolio'),avg_rating=Avg('booking__review__rating'),).order_by('-avg_rating', '-portfolio_count')
    )
    return render(request, 'core/photographers.html', {'photographers': photographers})


def photographer_public(request, pk):
    photographer = get_object_or_404(Photographer, pk=pk)
    portfolios = Portfolio.objects.filter(photographer=photographer)
    return render(request, 'accounts/photographer_public.html', {
        'photographer': photographer,
        'portfolios': portfolios,
    })


@login_required
@never_cache
def client_dashboard(request):
    if request.session.get('role') != 'client':
        raise PermissionDenied

    bookings_qs = Booking.objects.filter(client=request.user).order_by('-event_date')
    bookings = []
    for b in bookings_qs:
        has_review = hasattr(b, 'review')
        bookings.append({'obj': b, 'has_review': has_review})
    return render(request, 'accounts/client_dashboard.html', {'bookings': bookings})


def developer_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if request.session.get('role') != 'developer':
            raise PermissionDenied
        return func(request, *args, **kwargs)
    return wrapper


@login_required
@developer_required
@never_cache
def developer_dashboard(request):
    User = get_user_model()
    photographers = Photographer.objects.select_related('user').exclude(
    user__profile__role__in=['developer', 'client'])
    clients = User.objects.filter(profile__role='client').select_related('profile')
    developers = User.objects.filter(profile__role='developer').select_related('profile')
    return render(request, 'accounts/developer_dashboard.html', {
        'photographers': photographers,
        'clients': clients,
        'developers': developers,
    })


@login_required
@developer_required
@never_cache
def developer_delete_user(request, user_pk):
    User = get_user_model()
    user = get_object_or_404(User, pk=user_pk)
    try:
        if user.profile.role == 'developer':
            messages.error(request, 'You cannot delete developer accounts from this page.')
            return redirect('developer_dashboard')
    except Exception:
        pass
    if user == request.user:
        messages.error(request, 'You cannot delete your own developer account.')
        return redirect('developer_dashboard')

    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} deleted.')
        return redirect('developer_dashboard')

    return render(request, 'accounts/confirm_delete_user.html', {'user_obj': user})


def custom_403_view(request, exception=None):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)
    return redirect('login')


@login_required
@never_cache
def add_review(request, booking_pk):
    if request.session.get('role') != 'client':
        raise PermissionDenied

    booking = get_object_or_404(Booking, pk=booking_pk)
    if booking.client != request.user:
        raise PermissionDenied
    if booking.status != 'completed':
        messages.error(request, 'You can only review completed bookings.')
        return redirect('client_dashboard')
    if hasattr(booking, 'review'):
        messages.error(request, 'This booking already has a review.')
        return redirect('client_dashboard')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, 'Review submitted.')
            return redirect('client_dashboard')
    else:
        form = ReviewForm()

    return render(request, 'accounts/review_form.html', {'form': form, 'booking': booking})
@login_required
def book_photographer(request, photographer_id):
    # --- NEW SECURITY CHECK ---
    # 1. Block photographers from acting as clients
    if request.user.profile.role == 'photographer':
        messages.error(request, "Access Denied: Photographer accounts cannot book other photographers. Please log in as a Client.")
        # Redirect them away (change 'home' to your actual home or dashboard URL name)
        return redirect('home') 

    # 2. Find the photographer they are trying to book
    photographer = get_object_or_404(Photographer, id=photographer_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            # commit=False creates the object in memory, but doesn't hit the database yet
            booking = form.save(commit=False)
            
            # Securely attach the 'Behind the Scenes' IDs
            booking.client = request.user
            booking.photographer = photographer
            
            # Save it to the database
            booking.save()
            
            messages.success(request, f"Your booking request has been sent to {photographer.user.username}!")
            return redirect('client_dashboard') # Change this to wherever they should go
    else:
        # Show an empty form
        form = BookingForm()

    context = {
        'form': form,
        'photographer': photographer
    }
    return render(request, 'book_photographer.html', context)


@login_required
@never_cache
def add_review(request, booking_pk):
    if request.session.get('role') != 'client':
        raise PermissionDenied

    booking = get_object_or_404(Booking, pk=booking_pk)
    if booking.client != request.user:
        raise PermissionDenied
    if booking.status != 'completed':
        messages.error(request, 'You can only review completed bookings.')
        return redirect('client_dashboard')
    if hasattr(booking, 'review'):
        messages.error(request, 'This booking already has a review.')
        return redirect('client_dashboard')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, 'Review submitted.')
            return redirect('client_dashboard')
    else:
        form = ReviewForm()

    return render(request, 'accounts/review_form.html', {'form': form, 'booking': booking})