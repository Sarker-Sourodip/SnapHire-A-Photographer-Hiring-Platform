from django.db import transaction
from django.contrib.auth.models import User
from .models import Profile, Photographer

"""
Creates a new user account, their associated Profile, and optionally their Photographer setup safely using a database transaction.


    username (str): The desired username for the new account.
    password (str): The raw password (will be hashed before saving).
    email (str): The user's email address.
    role (str): The user type, typically 'client', 'photographer', or 'developer'.
    phone (str, optional): The user's phone number. Defaults to None.
    address (str, optional): The user's physical address. Defaults to None.
    profile_picture (file, optional): An uploaded image file for the user's avatar. Defaults to None.
    bio (str, optional): A short biography (Only used if role is 'photographer'). Defaults to None.
    experience_years (int, optional): Years of professional experience (Only used if role is 'photographer'). Defaults to 0.
    price_per_hour (decimal/float, optional): Hourly booking rate (Only used if role is 'photographer'). Defaults to 0.
    location (str, optional): Primary working location/city (Only used if role is 'photographer'). Defaults to None.


    This function utilizes `transaction.atomic()`. This ensures that creating the Base User, 
    creating the Profile, and creating the Photographer instance are treated as a single operation. 
    If any step fails (e.g., the Photographer instance crashes), the entire transaction rolls back, 
    preventing "orphan" or half-created user accounts in the database.

    
    This function is primarily called within `accounts/views.py`, specifically inside the 
    `register_view` (or equivalent registration function) when a new user successfully submits 
    the signup form via a POST request.

    
    tuple: (User object, boolean). The boolean is True if the user was successfully created, 
    and False if the creation failed or the user already existed.
"""
def create_user_safely(username, password, email, role, phone=None, address=None, profile_picture=None, bio=None, experience_years=0, price_per_hour=0, location=None):
    try:
        with transaction.atomic():
            user, created = User.objects.get_or_create(username=username, email=email)
            if not created:
                return user, False
            
            user.set_password(password)
            user.save()

            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            if phone: profile.phone = phone
            if address: profile.address = address
            if profile_picture: profile.profile_picture = profile_picture
            profile.save()

            if role == 'photographer':
                Photographer.objects.create(
                    user=user,
                    bio=bio,
                    experience_years=experience_years,
                    price_per_hour=price_per_hour,
                    location=location
                )

            return user, True
    except Exception as e:
        return None, False