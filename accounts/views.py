<<<<<<< HEAD
from django.shortcuts import render, redirect, get_object_or_404
=======
from django.shortcuts import render, redirect
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
<<<<<<< HEAD
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Avg, Count, Q, Value
from django.db.models.functions import Coalesce
from functools import wraps

from .forms import RegistrationForm, LoginForm, PhotographerForm, PortfolioForm, ReviewForm, BookingForm, PhotographerUpdateForm, ProfileUpdateForm
from .models import Photographer, Profile, Portfolio, Booking, Review
=======
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Avg, Count
from functools import wraps
from django.contrib import messages
from .models import Notification

from .forms import RegistrationForm, LoginForm, PhotographerForm, PortfolioForm, ReviewForm, BookingForm, PhotographerUpdateForm, ProfileUpdateForm
from .models import Photographer, Profile, Portfolio, Booking, Review, Notification
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09

# --- NEW: Import the Service ---
from .services import create_user_safely

def redirect_to_dashboard(request):
<<<<<<< HEAD
    """ Helper function to redirect users to their correct dashboard based on role. """
=======
    """
    Helper function to redirect users to their correct dashboard 
    based on their session role.
    """
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    role = request.session.get('role')
    if role == 'client':
        return redirect('photographers_list')
    elif role == 'photographer':
        return redirect('photographer_dashboard')
    elif role == 'developer':
        return redirect('developer_dashboard')
    return redirect('home')

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)

    if request.method == 'POST':
<<<<<<< HEAD
        form = RegistrationForm(request.POST, request.FILES) 
        if form.is_valid():
            requested_role = form.cleaned_data['role']
            final_role = 'client' if requested_role == 'developer' else requested_role

=======
        # MUST INCLUDE request.FILES for the profile picture!
        form = RegistrationForm(request.POST, request.FILES) 
        if form.is_valid():
            # Pass all the new data to the service
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
            user, created = create_user_safely(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
<<<<<<< HEAD
                role=final_role,
=======
                role=form.cleaned_data['role'],
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
                phone=form.cleaned_data.get('phone'),
                address=form.cleaned_data.get('address'),
                profile_picture=form.cleaned_data.get('profile_picture'),
                bio=form.cleaned_data.get('bio'),
                experience_years=form.cleaned_data.get('experience_years'),
                price_per_hour=form.cleaned_data.get('price_per_hour'),
                location=form.cleaned_data.get('location')
            )

            if not created:
                messages.error(request, 'Username already taken.')
                return render(request, 'accounts/register.html', {'form': form})

<<<<<<< HEAD
            login(request, user)
            request.session['role'] = user.profile.role
            messages.success(request, 'Registration successful!')
            return redirect_to_dashboard(request)
    else:
        form = RegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})

=======
            # Success path
            login(request, user)
            request.session['role'] = user.profile.role
            messages.success(request, 'Registration successful!')
            
            # Since they did everything on one page, skip setup and go straight to dashboard
            return redirect_to_dashboard(request)
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
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
            
<<<<<<< HEAD
=======
            # Save role to session
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
            try:
                request.session['role'] = user.profile.role
            except Exception:
                request.session['role'] = 'guest'

            return redirect_to_dashboard(request)
    else:
        form = LoginForm(request=request)

    return render(request, 'accounts/login.html', {'form': form})

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@never_cache
def logout_view(request):
    list(messages.get_messages(request))
    logout(request)
    return redirect('login')

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@login_required
@never_cache
def photographer_setup(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer, created = Photographer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
<<<<<<< HEAD
=======
        # Grab data for both forms
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        ph_form = PhotographerUpdateForm(request.POST, instance=photographer)
        
        if p_form.is_valid() and ph_form.is_valid():
            p_form.save()
            ph_form.save()
            messages.success(request, 'Profile settings updated successfully!')
            return redirect('photographer_dashboard')
    else:
<<<<<<< HEAD
        p_form = ProfileUpdateForm(instance=request.user.profile)
        ph_form = PhotographerUpdateForm(instance=photographer)

    return render(request, 'accounts/photographer_setup.html', {'p_form': p_form, 'ph_form': ph_form})

=======
        # Pre-fill with existing data
        p_form = ProfileUpdateForm(instance=request.user.profile)
        ph_form = PhotographerUpdateForm(instance=photographer)

    # Pass BOTH forms to the template
    return render(request, 'accounts/photographer_setup.html', {'p_form': p_form, 'ph_form': ph_form})


>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@login_required
@never_cache
def photographer_dashboard(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer, created = Photographer.objects.get_or_create(user=request.user)
<<<<<<< HEAD

    # --- NEW: LAZY SWEEP (AUTO-DECLINE) ---
    # Automatically reject any 'pending' bookings that have already passed
    Booking.objects.filter(
        photographer=photographer,
        status='pending',
        event_date__lt=timezone.now()
    ).update(status='rejected')
    # --------------------------------------

    portfolios = Portfolio.objects.filter(photographer=photographer)
    bookings = Booking.objects.filter(photographer=photographer).order_by('-created_at')

    reviews = Review.objects.filter(booking__photographer=photographer).order_by('-created_at')
    stats = reviews.aggregate(Avg('rating'))
    calculated_rating = stats['rating__avg'] or 0.0

    return render(request, 'accounts/photographer_dashboard.html', {
        'photographer': photographer,
        'portfolios': portfolios,
        'bookings': bookings,
        'reviews': reviews,
        'avg_rating': calculated_rating,
        'now': timezone.now(), # <--- FIXED: Passes current time to let template conditionally block finish button
    })

=======
    portfolios = Portfolio.objects.filter(photographer=photographer)
    
    # NEW: Get all bookings for this photographer, newest first
    bookings = Booking.objects.filter(photographer=photographer).order_by('-created_at')

    return render(request, 'accounts/photographer_dashboard.html', {
        'photographer': photographer,
        'portfolios': portfolios,
        'bookings': bookings, # Pass bookings to the HTML
    })


>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@login_required
@never_cache
def portfolio_list(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer = Photographer.objects.get(user=request.user)
    items = Portfolio.objects.filter(photographer=photographer)
    return render(request, 'accounts/portfolio_list.html', {'items': items})

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
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

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
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

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
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

<<<<<<< HEAD
def photographers_list(request):
    # --- STRICT SECURITY GUARD ---
    if request.user.is_authenticated:
        role = request.session.get('role')
        
        if role == 'photographer':
            messages.warning(request, "You are logged in as a Creator. You cannot browse the client directory.")
            return redirect('photographer_dashboard')
            
        elif role == 'developer':
            messages.warning(request, "Developer accounts cannot browse the public directory. Please use your admin tools.")
            return redirect('developer_dashboard')
    # -----------------------------

    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

=======

def photographers_list(request):
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    photographers = (
        Photographer.objects.select_related('user')
        .filter(user__profile__role='photographer')
        .prefetch_related('portfolio_set')
        .annotate(
            portfolio_count=Count('portfolio'),
<<<<<<< HEAD
            calculated_rating=Coalesce(Avg('photographer_bookings__review__rating'), Value(0.0))
        )
    )

    if search_query:
        photographers = photographers.filter(
            Q(user__username__icontains=search_query) |
            Q(bio__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if sort_by == 'rating_desc':
        photographers = photographers.order_by('-calculated_rating', '-portfolio_count')
    elif sort_by == 'rating_asc':
        photographers = photographers.order_by('calculated_rating', '-portfolio_count')
    elif sort_by == 'price_desc':
        photographers = photographers.order_by('-price_per_hour')
    elif sort_by == 'price_asc':
        photographers = photographers.order_by('price_per_hour')
    else:
        photographers = photographers.order_by('-calculated_rating', '-portfolio_count')

    return render(request, 'accounts/photographers.html', {
        'photographers': photographers,
        'search_query': search_query,
        'sort_by': sort_by,
    })

def photographer_public(request, pk):
    # --- STRICT SECURITY GUARD ---
    if request.user.is_authenticated:
        role = request.session.get('role')
        
        if role == 'photographer':
            messages.warning(request, "You are logged in as a Creator. You cannot view client-facing profiles.")
            return redirect('photographer_dashboard')
            
        elif role == 'developer':
            messages.warning(request, "Developer accounts cannot browse public profiles. Please use your admin tools.")
            return redirect('developer_dashboard')
    # -----------------------------

    # Your original logic is completely untouched below:
    photographer = get_object_or_404(Photographer, pk=pk)
    portfolios = Portfolio.objects.filter(photographer=photographer)
    
    reviews = Review.objects.filter(booking__photographer=photographer).select_related('booking__client').order_by('-created_at')
=======
            # CHANGED: 'booking' is now 'photographer_bookings'
            avg_rating=Avg('photographer_bookings__review__rating'),
        )
        .order_by('-avg_rating', '-portfolio_count')
    )
    return render(request, 'accounts/photographers.html', {'photographers': photographers})


def photographer_public(request, pk):
    photographer = get_object_or_404(Photographer, pk=pk)
    portfolios = Portfolio.objects.filter(photographer=photographer)
    
    # NEW: Fetch all reviews for this photographer, newest first
    # select_related makes the database query much faster since we need the client's username
    reviews = Review.objects.filter(booking__photographer=photographer).select_related('booking__client').order_by('-created_at')
    
    # NEW: Calculate the average rating (out of 5)
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'accounts/photographer_public.html', {
        'photographer': photographer,
        'portfolios': portfolios,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@login_required
@never_cache
def client_dashboard(request):
    if request.session.get('role') != 'client':
        raise PermissionDenied

<<<<<<< HEAD
    # --- NEW: LAZY SWEEP (AUTO-DECLINE) ---
    # Automatically reject any 'pending' bookings that have already passed
    Booking.objects.filter(
        client=request.user,
        status='pending',
        event_date__lt=timezone.now()
    ).update(status='rejected')
    # --------------------------------------

=======
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    bookings_qs = Booking.objects.filter(client=request.user).order_by('-event_date')
    bookings = []
    for b in bookings_qs:
        has_review = hasattr(b, 'review')
        bookings.append({'obj': b, 'has_review': has_review})
<<<<<<< HEAD
        
    return render(request, 'accounts/client_dashboard.html', {'bookings': bookings})

=======
    return render(request, 'accounts/client_dashboard.html', {'bookings': bookings})


>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@login_required
@never_cache
def client_setup(request):
    if request.session.get('role') != 'client':
        raise PermissionDenied

    if request.method == 'POST':
<<<<<<< HEAD
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
=======
        # We can reuse the exact same ProfileUpdateForm we made earlier!
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('client_dashboard')
    else:
<<<<<<< HEAD
=======
        # Pre-fill the form with their current data
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/client_setup.html', {'form': form})

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
def developer_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if request.session.get('role') != 'developer':
            raise PermissionDenied
        return func(request, *args, **kwargs)
    return wrapper

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
@login_required
@developer_required
@never_cache
def developer_dashboard(request):
    User = get_user_model()
<<<<<<< HEAD
    photographers = Photographer.objects.select_related('user').exclude(user__profile__role__in=['developer', 'client'])
=======
    photographers = Photographer.objects.select_related('user').exclude(
    user__profile__role__in=['developer', 'client'])
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    clients = User.objects.filter(profile__role='client').select_related('profile')
    developers = User.objects.filter(profile__role='developer').select_related('profile')
    return render(request, 'accounts/developer_dashboard.html', {
        'photographers': photographers,
        'clients': clients,
        'developers': developers,
    })

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
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

<<<<<<< HEAD
=======

>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
def custom_403_view(request, exception=None):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)
    return redirect('login')

<<<<<<< HEAD
@login_required
def book_photographer(request, photographer_id):
    # 1. Block photographers from acting as clients
    if request.user.profile.role == 'photographer':
        messages.error(request, "Access Denied: Photographer accounts cannot book other photographers. Please log in as a Client.")
        return redirect('home') 

    # 2. Find the photographer
    photographer = get_object_or_404(Photographer, id=photographer_id)

    # --- FEATURE 1: PREVENT DOUBLE BOOKING ---
    has_active_booking = Booking.objects.filter(
        client=request.user,
        photographer=photographer,
        status__in=['pending', 'accepted']
    ).exists()

    if has_active_booking:
        messages.warning(request, f"You already have an active booking request with {photographer.user.username}. Please wait for it to be completed before booking them again.")
        return redirect('client_dashboard')
    # -----------------------------------------

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            # --- FEATURE 2: FUTURE TIME LOCK ---
            if booking.event_date < timezone.now():
                messages.error(request, "Failed: Your event date and time must be explicitly in the future!")
                return render(request, 'accounts/book_photographer.html', {'form': form, 'photographer': photographer})
            # -----------------------------------
            
            booking.client = request.user
            booking.photographer = photographer
            booking.save()
            messages.success(request, f"Your booking request has been sent to {photographer.user.username}!")
            return redirect('client_dashboard') 
    else:
        form = BookingForm()

    context = {
        'form': form,
        'photographer': photographer
    }
    return render(request, 'accounts/book_photographer.html', context)
=======
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09

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

<<<<<<< HEAD
@login_required
def update_booking_status(request, booking_id, status):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied
    
    booking = get_object_or_404(Booking, id=booking_id, photographer__user=request.user)
    
    if status in ['accepted', 'rejected', 'completed']:
        
        # --- FIXED: Rigid system restriction locking job finalization before event arrival ---
        if status == 'completed' and booking.event_date > timezone.now():
            messages.error(request, "Access Blocked: You cannot finish this job before the scheduled event date and time!")
            return redirect('photographer_dashboard')
            
        booking.status = status
        booking.save()
        messages.success(request, f"Booking has been marked as {status.title()}!")
        
    return redirect('photographer_dashboard')
=======

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
    return render(request, 'accounts/book_photographer.html', context)


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
def update_booking_status(request, booking_id, status):
    """ Allows photographers to accept or reject a booking """
    if request.session.get('role') != 'photographer':
        raise PermissionDenied
    
    # Ensure they only edit THEIR bookings
    booking = get_object_or_404(Booking, id=booking_id, photographer__user=request.user)
    
    # Security check: only allow valid statuses
    if status in ['accepted', 'rejected', 'completed']:
        booking.status = status
        booking.save()

        # Create notification for client

        if status == 'accepted':
            Notification.objects.create(
                user=booking.client,
                message=f"Your booking with {booking.photographer.user.username} was accepted."
            )

        elif status == 'rejected':
            Notification.objects.create(
                user=booking.client,
                message=f"Your booking with {booking.photographer.user.username} was rejected."
            )

        elif status == 'completed':
            Notification.objects.create(
                user=booking.client,
                message=f"Your booking with {booking.photographer.user.username} was completed."
            )

        if status == 'accepted':
            messages.success(
                request,
                f"You accepted the booking from {booking.client.username}."
            )

        elif status == 'rejected':
            messages.warning(
                request,
                f"You rejected the booking from {booking.client.username}."
            )

        elif status == 'completed':
            messages.success(
                request,
                "Booking marked as completed successfully!"
            )
        
    return redirect('photographer_dashboard')

@login_required
def notifications(request):
    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'accounts/notifications.html', {
        'notifications': notifications
    })



def notification_count(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()

        return {'notification_count': count}

    return {'notification_count': 0}
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
