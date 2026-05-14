from django.db import transaction
from django.contrib.auth.models import User
from .models import Profile, Photographer

def create_user_safely(username, password, email, role, **extra_fields):
    """
    The Single Channel for user creation. 
    Now automatically handles Admin access for Developers.
    """
    with transaction.atomic():
        # 1. Get or Create the User
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={'email': email}
        )

        # 2. Set Password & Status
        if user_created:
            user.set_password(password)
        
        # --- NEW PERMISSION LOGIC ---
        if role == 'developer':
            user.is_staff = True
            user.is_superuser = True  # Give them full power
        else:
            # Ensure non-developers don't accidentally get staff access
            user.is_staff = False
            user.is_superuser = False
            
        user.save()
            
        # 3. Handle the Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.role = role
        profile.save()
        
        # 4. Handle Photographer specific record
        if role == 'photographer':
            Photographer.objects.get_or_create(user=user)
        
        return user, user_created