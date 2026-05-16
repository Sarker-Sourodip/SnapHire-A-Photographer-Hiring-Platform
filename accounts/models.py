from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

class Profile(models.Model):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('photographer', 'Photographer'),
        ('developer', 'Developer'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='profile_pictures/default.jpg', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Photographer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username

class Portfolio(models.Model):
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='portfolio/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.photographer.user.username} Portfolio"

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

<<<<<<< HEAD
    # Relationships
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE, related_name='photographer_bookings')
    
    # Core Booking Details
    event_date = models.DateTimeField() # Upgraded to track exact time!
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True) # Renamed to match forms.py
    
    # State Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Timestamps
=======
    PAYMENT_CHOICES = (
        ('unpaid', 'Unpaid'),
        ('partial', 'Partial Deposit'),
        ('paid', 'Fully Paid'),
        ('refunded', 'Refunded'),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE, related_name='photographer_bookings')
    
    event_date = models.DateField()
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    message = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='unpaid')
    
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
<<<<<<< HEAD
        # Now shows the date in the admin panel (e.g., "ClientName → PhotoName (Oct 12, 2026)")
        return f"{self.client.username} → {self.photographer.user.username} ({self.event_date.strftime('%b %d, %Y')})"
=======
        return f"{self.client.username} → {self.photographer.user.username}"
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking.photographer.user.username}"


@receiver(post_delete, sender=Portfolio)
def delete_portfolio_image_on_delete(sender, instance, **kwargs):
    if not instance.image:
        return
    storage = instance.image.storage
    name = instance.image.name
    try:
        if name and storage.exists(name):
            storage.delete(name)
    except (FileNotFoundError, OSError) as e:
        logger.warning("Failed deleting portfolio image %s: %s", name, e)
    except Exception:
        logger.exception("Unexpected error deleting portfolio image %s", name)

@receiver(pre_save, sender=Portfolio)
def delete_old_portfolio_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Portfolio.objects.get(pk=instance.pk)
    except Portfolio.DoesNotExist:
        return
    old_file = old.image
    new_file = instance.image
    if not old_file or old_file == new_file:
        return

    storage = old_file.storage
    name = old_file.name
    try:
        if name and storage.exists(name):
            storage.delete(name)
    except (FileNotFoundError, OSError) as e:
        logger.warning("Failed removing old portfolio image %s: %s", name, e)
    except Exception:
        logger.exception("Unexpected error removing old portfolio image %s", name)


@receiver(post_delete, sender=Profile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    """Deletes the profile picture when the user account is deleted."""
    if not instance.profile_picture:
        return
        
    # STOP! Never delete the default image!
    if instance.profile_picture.name == 'profile_pictures/default.jpg':
        return
        
    storage = instance.profile_picture.storage
    name = instance.profile_picture.name
    try:
        if name and storage.exists(name):
            storage.delete(name)
    except (FileNotFoundError, OSError) as e:
        logger.warning("Failed deleting profile picture %s: %s", name, e)
    except Exception:
        logger.exception("Unexpected error deleting profile picture %s", name)


@receiver(pre_save, sender=Profile)
def delete_old_profile_picture_on_change(sender, instance, **kwargs):
    """Deletes the old profile picture when a user uploads a new one."""
    if not instance.pk:
        return
    try:
        old = Profile.objects.get(pk=instance.pk)
    except Profile.DoesNotExist:
        return
        
    old_file = old.profile_picture
    new_file = instance.profile_picture
    
    if not old_file or old_file == new_file:
        return

    # STOP! Never delete the default image!
    if old_file.name == 'profile_pictures/default.jpg':
        return

    storage = old_file.storage
    name = old_file.name
    try:
        if name and storage.exists(name):
            storage.delete(name)
    except (FileNotFoundError, OSError) as e:
        logger.warning("Failed removing old profile picture %s: %s", name, e)
    except Exception:
<<<<<<< HEAD
        logger.exception("Unexpected error removing old profile picture %s", name)
=======
        logger.exception("Unexpected error removing old profile picture %s", name)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
