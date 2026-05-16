from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile, Portfolio, Review, Photographer, Booking

class RegistrationForm(forms.ModelForm): # Assuming you are using ModelForm for User
    password1 = forms.CharField(label = "Password",widget=forms.PasswordInput(attrs={'class': 'form-control'}))
<<<<<<< HEAD
    password_confirm = forms.CharField(label = "Confirm Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
=======
    password_confirm = forms.CharField(label = "Conform Password", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, widget=forms.Select(attrs={'class': 'form-select', 'id': 'role-select'}))

    # --- Profile Fields ---
    phone = forms.CharField(max_length=15, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    # --- Photographer Fields (Hidden by default in HTML) ---
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

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')

        # If they register as a photographer, strictly enforce these fields
        if role == 'photographer':
            if not cleaned_data.get('profile_picture'):
                self.add_error('profile_picture', 'Photographers must upload a profile picture.')
            if not cleaned_data.get('location'):
                self.add_error('location', 'Location is required for photographers.')
            if not cleaned_data.get('price_per_hour'):
                self.add_error('price_per_hour', 'Please set your hourly rate.')
            
        return cleaned_data

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class PhotographerForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone', 'address']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # THIS IS THE MAGIC LINE: It forces the photographer to upload a picture
        self.fields['profile_picture'].required = True
        
        # Optional: Add Bootstrap classes to make it look nice
        self.fields['profile_picture'].widget.attrs.update({'class': 'form-control'})


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['image', 'description']


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture', 'phone', 'address']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


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


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
<<<<<<< HEAD
        # CHANGED: 'message' is now 'notes' to match the updated models.py
        fields = ['event_date', 'event_type', 'location', 'notes']
        
        # Widgets make the HTML look nice and add things like the date-picker calendar
        widgets = {
            # CHANGED: Now uses DateTimeInput and 'datetime-local' to capture the exact hour/minute
            'event_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local', 
=======
        fields = ['event_date', 'event_type', 'location', 'message']
        
        # Widgets make the HTML look nice and add things like the date-picker calendar
        widgets = {
            'event_date': forms.DateInput(attrs={
                'type': 'date', 
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
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
<<<<<<< HEAD
            # CHANGED: Key is now 'notes' instead of 'message'
            'notes': forms.Textarea(attrs={
=======
            'message': forms.Textarea(attrs={
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Tell the photographer about your vision, schedule, and any special requests...'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']