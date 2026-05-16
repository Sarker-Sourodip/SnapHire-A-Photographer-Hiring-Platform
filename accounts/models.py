from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import logging

logger = logging.getLogger(__name__)

"""
Extends the default Django Base User model to store platform-specific identity information.
It links one-to-one with the Base User and holds the account's primary role (client, 
photographer, or developer), alongside basic contact details and an avatar.
This model is accessed globally across the application to determine user permissions, 
route dashboards, and display profile headers.
"""
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


"""
Stores professional and business-specific details for accounts registered with the 
'photographer' role. It expands on the Base User to include their biography, years 
of professional experience, hourly booking rate, and operational city.
This data is primarily queried by the public directory views to render search results, 
sort creators, and populate the public-facing portfolio pages.
"""
class Photographer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    experience_years = models.IntegerField(default=0)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.user.username


"""
Represents a single image upload within a photographer's public gallery.
It links directly to a specific Photographer instance and holds the physical image 
file, an optional description, and an automatic timestamp of when it was uploaded.
It is primarily used to render the visual grid on a photographer's public profile 
page to showcase their work to potential clients.
"""
class Portfolio(models.Model):
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='portfolio/')
    description = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.photographer.user.username} Portfolio"


"""
Manages the reservation and lifecycle of a photoshoot event between a client and a photographer.
It tracks the two related users, the event's schedule, location, specific client notes, 
and the current state of the request (pending, accepted, rejected, or completed).
This model serves as the core engine for both the Client and Photographer dashboards, 
allowing both parties to manage their upcoming schedules and historical jobs.
"""
class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_bookings')
    photographer = models.ForeignKey(Photographer, on_delete=models.CASCADE, related_name='photographer_bookings')
    
    event_date = models.DateTimeField()
    event_type = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.username} → {self.photographer.user.username} ({self.event_date.strftime('%b %d, %Y')})"


"""
Stores client feedback and a star rating for a successfully completed photoshoot.
It has a strict one-to-one relationship with a Booking, ensuring that only actual 
clients can leave exactly one review per completed job.
These records are aggregated to calculate a photographer's overall score on the 
browse page and are displayed chronologically on their public profile.
"""
class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking.photographer.user.username}"


"""
A Django post_delete signal receiver that automatically performs cleanup operations 
on the server's file system.
It is triggered automatically whenever a Portfolio database record is deleted.
It finds the physical image file associated with the deleted database entry and 
removes it from the storage folder, preventing orphaned files from consuming server space.
"""
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


"""
A Django pre_save signal receiver designed to manage file updates cleanly.
It is triggered automatically just before an existing Portfolio database record is updated.
It compares the incoming new file with the existing old file. If the photographer 
is replacing the image, it deletes the old physical file from the server before 
the new one is saved, avoiding storage bloat.
"""
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


"""
A Django post_delete signal receiver responsible for cleaning up user avatars.
It is triggered automatically whenever a user's Profile record is deleted (which 
usually happens when the Base User account is deleted).
It locates the user's custom profile picture and physically deletes it from the server, 
with a hardcoded safety check to ensure it never deletes the platform's default placeholder image.
"""
@receiver(post_delete, sender=Profile)
def delete_profile_picture_on_delete(sender, instance, **kwargs):
    if not instance.profile_picture:
        return
        
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


"""
A Django pre_save signal receiver that prevents abandoned avatars from accumulating.
It is triggered automatically right before a user saves changes to their Profile.
If the system detects that the user has uploaded a new profile picture to replace 
an old one, it deletes the previous custom image file from the server. It actively 
ignores the transaction if the previous image was the system's default placeholder.
"""
@receiver(pre_save, sender=Profile)
def delete_old_profile_picture_on_change(sender, instance, **kwargs):
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
        logger.exception("Unexpected error removing old profile picture %s", name)