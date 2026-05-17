from django.db import transaction
from django.contrib.auth.models import User
from .models import Profile, Photographer

def create_user_safely(username, password, email, role, phone=None, address=None, profile_picture=None, bio=None, experience_years=0, price_per_hour=0, location=None):
    try:
        with transaction.atomic():
            # 1. Create User
            user, created = User.objects.get_or_create(username=username, email=email)
            if not created:
                return user, False
            
            user.set_password(password)
            user.save()

            # 2. Update Profile (It might be auto-created by signals, so we get_or_create)
            profile, _ = Profile.objects.get_or_create(user=user)
            profile.role = role
            if phone: profile.phone = phone
            if address: profile.address = address
            if profile_picture: profile.profile_picture = profile_picture
            profile.save()

            # 3. If Photographer, Create Photographer record
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