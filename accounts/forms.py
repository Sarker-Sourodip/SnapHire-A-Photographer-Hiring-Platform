from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Profile
from .models import Photographer
from .models import Portfolio, Review

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


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']