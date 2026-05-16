from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile, Portfolio, Review, Photographer, Booking

"""
Handles the comprehensive registration process for all new platform users.
It collects core authentication details (username, email, passwords), general 
profile information (role, phone, address, profile_picture), and optionally 
professional photographer metrics (bio, experience_years, price_per_hour, location).
This form is utilized exclusively on the main registration page to gather all 
necessary data into a single POST request before passing it to the backend 
user creation logic.
"""
class RegistrationForm(forms.ModelForm): 
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'id': 'role-select'}))

    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    bio = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    experience_years = forms.IntegerField(required=False, initial=0, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    price_per_hour = forms.DecimalField(required=False, max_digits=10, decimal_places=2, initial=0.00, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    location = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))


    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


    """
    Performs custom validation on the submitted registration data before processing.
    It evaluates the selected account role and dynamically applies strict validation rules. 
    If the user registers as a 'photographer', it intercepts the submission to verify 
    that a profile picture, location, and hourly rate were explicitly provided, appending 
    errors to the form if the data is missing.
    """
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        if role == 'photographer':
            if not cleaned_data.get('profile_picture'):
                self.add_error('profile_picture', 'Photographers must upload a profile picture.')
            if not cleaned_data.get('location'):
                self.add_error('location', 'Location is required for photographers.')
            if not cleaned_data.get('price_per_hour'):
                self.add_error('price_per_hour', 'Please set your hourly rate.')
            
        return cleaned_data


"""
Facilitates standard user authentication by extending Django's built-in AuthenticationForm.
It captures the username and password inputs required to verify credentials against 
the database. This form is rendered on the primary login page to establish a secure 
user session and route them to their appropriate dashboard.
"""
class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


"""
Manages a specialized subset of Profile data, specifically prioritizing the upload 
of a user's avatar alongside basic contact details (phone and address).
It is typically utilized in onboarding flows or setup views where a profile picture 
needs to be strictly enforced before a photographer can proceed.
"""
class PhotographerForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone', 'address']


    """
    Intercepts the initialization of the form instance to dynamically alter field attributes.
    It accesses the 'profile_picture' field directly to flip its 'required' status to True, 
    ensuring the form cannot be submitted without an image. It also injects Bootstrap 
    CSS classes into the widget for consistent frontend styling.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['profile_picture'].required = True
        
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})


"""
Handles the submission of individual work samples for a creator's public gallery.
It collects an image file and an optional text description, tying them to the Portfolio model.
This is implemented in the photographer dashboard to allow users to dynamically grow 
their visible body of work on their public profile.
"""
class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['image', 'description']


"""
Allows existing users to safely modify their overarching identity parameters.
It binds to the Profile model to collect updates for the profile picture, phone number, 
and physical address, applying standard HTML constraints and CSS classes. 
This form powers the general account settings page for both clients and photographers.
"""
class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


"""
Permits active creators to update their business-specific metadata.
It connects to the Photographer model to capture revisions to their biography, 
years of experience, billing rate, and operational location.
This form is rendered inside the photographer dashboard's profile editing section 
to ensure their public directory listing remains accurate.
"""
class PhotographerUpdateForm(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = ['bio', 'experience_years', 'price_per_hour', 'location']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'price_per_hour': forms.NumberInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
        }


"""
Facilitates the creation of a new job request from a client to a photographer.
It captures the proposed event date, the type of occasion, the physical location, 
and any specific vision notes the client wants to provide.
This form is rendered directly on a creator's public profile page, acting as the 
primary tool for initiating the platform's booking lifecycle.
"""
class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['event_date', 'event_type', 'location', 'notes']
        
        widgets = {
            'event_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
                'class': 'form-control'
            }),
            'event_type': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'e.g., Wedding, Birthday, Corporate Portrait'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Full address or venue name'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Tell the photographer about your vision, schedule, and any special requests...'
            }),
        }


"""
Collects post-event feedback from clients after a job reaches the 'completed' status.
It is bound to the Review model to take in a numeric rating and written commentary.
This form is served within the client dashboard to help build aggregate scores 
and public testimonials for the photographers.
"""
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']