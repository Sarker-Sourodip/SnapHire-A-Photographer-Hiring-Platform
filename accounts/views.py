from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Avg, Count, Q, Value
from django.db.models.functions import Coalesce
from functools import wraps

from .forms import RegistrationForm, LoginForm, PhotographerForm, PortfolioForm, ReviewForm, BookingForm, PhotographerUpdateForm, ProfileUpdateForm
from .models import Photographer, Profile, Portfolio, Booking, Review
from .services import create_user_safely


"""
Routes authenticated users to their respective dashboards based on the role stored in their current session. 
It evaluates the session variable and maps it to the correct URL routing name. This is utilized dynamically 
after a successful login, registration, or when intercepting unauthorized page access to ensure users 
always land on their appropriate homepage.
"""
def redirect_to_dashboard(request):
    role = request.session.get('role')
    if role == 'client':
        return redirect('photographers_list')
    elif role == 'photographer':
        return redirect('photographer_dashboard')
    elif role == 'developer':
        return redirect('developer_dashboard')
    return redirect('home')


"""
Manages the creation of new user accounts by processing the registration form data. 
It accepts user credentials, contact details, profile imagery, and role-specific metrics. 
It delegates the actual database saving to the secure transaction method, establishes the active session 
upon success, blocks already logged-in users from accessing the page, and routes new users to their dashboard. 
It serves as the core endpoint for platform onboarding.
"""
@never_cache
def register(request):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)

    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES) 
        if form.is_valid():
            requested_role = form.cleaned_data['role']
            final_role = 'client' if requested_role == 'developer' else requested_role

            user, created = create_user_safely(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                role=final_role,
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

            login(request, user)
            request.session['role'] = user.profile.role
            messages.success(request, 'Registration successful!')
            return redirect_to_dashboard(request)
    else:
        form = RegistrationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


"""
Authenticates existing users and initializes their platform session. 
It accepts a username and password via a POST request, validates them against the database, 
securely sets the role identifier within the session variables, and routes the user to the correct interface. 
It actively prevents logged-in users from viewing the login screen again.
"""
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
            
            try:
                request.session['role'] = user.profile.role
            except Exception:
                request.session['role'] = 'guest'

            return redirect_to_dashboard(request)
    else:
        form = LoginForm(request=request)

    return render(request, 'accounts/login.html', {'form': form})


"""
Terminates the current user's active session. 
It accepts the request object, forces the clearance of any pending notification messages, 
destroys the authentication tokens, and redirects the user safely back to the login screen.
"""
@never_cache
def logout_view(request):
    list(messages.get_messages(request))
    logout(request)
    return redirect('login')


"""
Allows photographers to update their foundational profile and professional business metrics simultaneously. 
It verifies the active session role, loads both the Profile and Photographer models for the logged-in user, 
and processes two separate update forms at once. It is utilized exclusively within the creator dashboard's settings.
"""
@login_required
@never_cache
def photographer_setup(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer, created = Photographer.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        ph_form = PhotographerUpdateForm(request.POST, instance=photographer)
        
        if p_form.is_valid() and ph_form.is_valid():
            p_form.save()
            ph_form.save()
            messages.success(request, 'Profile settings updated successfully!')
            return redirect('photographer_dashboard')
    else:
        p_form = ProfileUpdateForm(instance=request.user.profile)
        ph_form = PhotographerUpdateForm(instance=photographer)

    return render(request, 'accounts/photographer_setup.html', {'p_form': p_form, 'ph_form': ph_form})


"""
Renders the primary control center for photographer accounts. 
It ensures strict role access, automatically executes a cleanup query to reject any pending bookings 
that have expired past their event date, and compiles the creator's portfolio items, historical bookings, 
and incoming reviews while dynamically calculating their aggregate star rating.
"""
@login_required
@never_cache
def photographer_dashboard(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer, created = Photographer.objects.get_or_create(user=request.user)

    Booking.objects.filter(
        photographer=photographer,
        status='pending',
        event_date__lt=timezone.now()
    ).update(status='rejected')

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
        'now': timezone.now(),
    })


"""
Retrieves and displays a visual grid of all portfolio images uploaded by the logged-in creator. 
It accesses the Portfolio model filtered by the active user's identity to populate the gallery management screen.
"""
@login_required
@never_cache
def portfolio_list(request):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied

    photographer = Photographer.objects.get(user=request.user)
    items = Portfolio.objects.filter(photographer=photographer)
    return render(request, 'accounts/portfolio_list.html', {'items': items})


"""
Handles the submission and storage of new visual assets to a creator's public gallery. 
It processes the uploaded file and text description, linking the new Portfolio record explicitly 
to the active photographer before redirecting them back to their dashboard.
"""
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


"""
Permits a photographer to modify an existing portfolio entry. 
It fetches the specific asset via its primary key, ensures it belongs to the authenticated user, 
and updates the corresponding image file or descriptive text through a POST request.
"""
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


"""
Removes a specific image asset from a creator's gallery and triggers the file cleanup signals. 
It requires the asset's primary key, verifies ownership, and necessitates a POST confirmation 
to execute the permanent deletion from the database.
"""
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


"""
Generates the comprehensive public directory of all active creators. 
It actively restricts access to prevent non-clients from browsing. It accepts query strings to filter results 
by name or location, applies sorting algorithms based on price or dynamic rating calculations, 
and leverages complex database aggregations to optimize the retrieval of portfolio sizes and review scores.
"""
def photographers_list(request):
    if request.user.is_authenticated:
        role = request.session.get('role')
        
        if role == 'photographer':
            messages.warning(request, "You are logged in as a Creator. You cannot browse the client directory.")
            return redirect('photographer_dashboard')
            
        elif role == 'developer':
            messages.warning(request, "Developer accounts cannot browse the public directory. Please use your admin tools.")
            return redirect('developer_dashboard')

    search_query = request.GET.get('q', '')
    sort_by = request.GET.get('sort', '')

    photographers = (
        Photographer.objects.select_related('user')
        .filter(user__profile__role='photographer')
        .prefetch_related('portfolio_set')
        .annotate(
            portfolio_count=Count('portfolio'),
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


"""
Renders the detailed public-facing portfolio and review history of a singular creator. 
It blocks access from other platform accounts, accepts the targeted photographer's primary key, 
and retrieves all associated image assets alongside a chronologically sorted list of client testimonials.
"""
def photographer_public(request, pk):
    if request.user.is_authenticated:
        role = request.session.get('role')
        
        if role == 'photographer':
            messages.warning(request, "You are logged in as a Creator. You cannot view client-facing profiles.")
            return redirect('photographer_dashboard')
            
        elif role == 'developer':
            messages.warning(request, "Developer accounts cannot browse public profiles. Please use your admin tools.")
            return redirect('developer_dashboard')

    photographer = get_object_or_404(Photographer, pk=pk)
    portfolios = Portfolio.objects.filter(photographer=photographer)
    
    reviews = Review.objects.filter(booking__photographer=photographer).select_related('booking__client').order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']

    return render(request, 'accounts/photographer_public.html', {
        'photographer': photographer,
        'portfolios': portfolios,
        'reviews': reviews,
        'avg_rating': avg_rating,
    })


"""
Serves as the primary operational hub for client accounts. 
It enforces role authorization, automatically updates the status of expired, unanswered booking requests to rejected, 
and aggregates all of the client's past and pending reservations, dynamically checking if a completed job 
is still eligible to receive a review.
"""
@login_required
@never_cache
def client_dashboard(request):
    if request.session.get('role') != 'client':
        raise PermissionDenied

    Booking.objects.filter(
        client=request.user,
        status='pending',
        event_date__lt=timezone.now()
    ).update(status='rejected')

    bookings_qs = Booking.objects.filter(client=request.user).order_by('-event_date')
    bookings = []
    for b in bookings_qs:
        has_review = hasattr(b, 'review')
        bookings.append({'obj': b, 'has_review': has_review})
        
    return render(request, 'accounts/client_dashboard.html', {'bookings': bookings})


"""
Allows standard clients to alter their personal contact information and avatar. 
It ensures the user maintains a client role and updates the underlying Profile model directly 
from a POST request before routing them back to their primary hub.
"""
@login_required
@never_cache
def client_setup(request):
    if request.session.get('role') != 'client':
        raise PermissionDenied

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('client_dashboard')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'accounts/client_setup.html', {'form': form})


"""
A custom authorization wrapper that strictly limits function execution to users holding the developer role. 
It evaluates the session state prior to executing the targeted view, raising a hard permission denial 
if any unauthorized user attempts access.
"""
def developer_required(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied
        if request.session.get('role') != 'developer':
            raise PermissionDenied
        return func(request, *args, **kwargs)
    return wrapper


"""
Provides a comprehensive administrative overview panel exclusively for developer accounts. 
It queries the database to segment and fetch lists of all registered photographers, clients, 
and fellow developers, facilitating high-level management and auditing of platform user bases.
"""
@login_required
@developer_required
@never_cache
def developer_dashboard(request):
    User = get_user_model()
    photographers = Photographer.objects.select_related('user').exclude(user__profile__role__in=['developer', 'client'])
    clients = User.objects.filter(profile__role='client').select_related('profile')
    developers = User.objects.filter(profile__role='developer').select_related('profile')
    return render(request, 'accounts/developer_dashboard.html', {
        'photographers': photographers,
        'clients': clients,
        'developers': developers,
    })


"""
Executes the permanent removal of a user account from the system by an administrator. 
It requires the targeted user's primary key and employs strict safety constraints to prevent the deletion 
of other developers or the administrator's own account. The deletion is finalized upon receiving a POST confirmation.
"""
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


"""
Intercepts application-wide permission denial errors to prevent users from seeing standard error pages. 
If an authenticated user strays into restricted territory, it safely redirects them back to their designed dashboard. 
If the user is a guest, they are routed to the login sequence.
"""
def custom_403_view(request, exception=None):
    if request.user.is_authenticated:
        return redirect_to_dashboard(request)
    return redirect('login')


"""
Initiates a new job reservation and communication lifecycle between a client and a photographer. 
It accepts the targeted creator's ID, verifies the initiator is a valid client, and checks the database 
to prevent duplicate pending requests. It aggressively validates that the proposed event timestamp 
is scheduled in the future before cementing the booking.
"""
@login_required
def book_photographer(request, photographer_id):
    if request.user.profile.role == 'photographer':
        messages.error(request, "Access Denied: Photographer accounts cannot book other photographers. Please log in as a Client.")
        return redirect('home') 

    photographer = get_object_or_404(Photographer, id=photographer_id)

    has_active_booking = Booking.objects.filter(
        client=request.user,
        photographer=photographer,
        status__in=['pending', 'accepted']
    ).exists()

    if has_active_booking:
        messages.warning(request, f"You already have an active booking request with {photographer.user.username}. Please wait for it to be completed before booking them again.")
        return redirect('client_dashboard')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            
            if booking.event_date < timezone.now():
                messages.error(request, "Failed: Your event date and time must be explicitly in the future!")
                return render(request, 'accounts/book_photographer.html', {'form': form, 'photographer': photographer})
            
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


"""
Captures post-event evaluation data and commentary from a client regarding a specific creator. 
It requires the booking ID, authenticates that the job is strictly marked as completed, ensures the user 
was the actual hiring client, and intercepts attempts to submit duplicate reviews for the same occasion.
"""
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


"""
Facilitates state management for an active reservation by the hired creator. 
It takes the booking ID and the desired status string (accepted, rejected, completed). 
It restricts execution to the photographer who owns the job, and enforces a chronological constraint 
preventing a task from being finalized as completed before the actual event date has occurred.
"""
@login_required
def update_booking_status(request, booking_id, status):
    if request.session.get('role') != 'photographer':
        raise PermissionDenied
    
    booking = get_object_or_404(Booking, id=booking_id, photographer__user=request.user)
    
    if status in ['accepted', 'rejected', 'completed']:
        
        if status == 'completed' and booking.event_date > timezone.now():
            messages.error(request, "Access Blocked: You cannot finish this job before the scheduled event date and time!")
            return redirect('photographer_dashboard')
            
        booking.status = status
        booking.save()
        messages.success(request, f"Booking has been marked as {status.title()}!")
        
    return redirect('photographer_dashboard')