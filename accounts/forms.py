from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile, Portfolio, Review, Photographer, Booking

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove roles that should not be selectable via public registration
        hidden = {'developer'}
        self.fields['role'].choices = [c for c in Profile.ROLE_CHOICES if c[0] not in hidden]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            profile, created = Profile.objects.get_or_create(user=user)
            profile.role = self.cleaned_data["role"]
            profile.save()
        return user

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError('This email is already in use.')
        return email

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput)


class PhotographerForm(forms.ModelForm):
    class Meta:
        model = Photographer
        fields = ['bio', 'experience_years', 'price_per_hour', 'location']


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['image', 'description']


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['event_date', 'event_type', 'location', 'message']
        
        # Widgets make the HTML look nice and add things like the date-picker calendar
        widgets = {
            'event_date': forms.DateInput(attrs={
                'type': 'date', 
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
            'message': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 4, 
                'placeholder': 'Tell the photographer about your vision, schedule, and any special requests...'
            }),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']