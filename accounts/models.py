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
    profile_picture = models.ImageField(upload_to='profile_pictures/', default='default.jpg', blank=True, null=True)

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
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.client.username} → {self.photographer.user.username}"

class Review(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking.photographer.user.username}"

# --- FILE CLEANUP SIGNALS ONLY ---

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