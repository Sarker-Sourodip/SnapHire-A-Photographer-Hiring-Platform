from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm  # Required for the custom form
from django.contrib.auth.models import User

from .models import Profile, Photographer, Portfolio, Booking, Review
<<<<<<< HEAD
from .services import create_user_safely 


"""
Modifies the default Django Admin user creation form by injecting a custom 'role' dropdown. 
It takes input directly from the administrator creating a user in the backend panel. 
This ensures that new users created manually by staff are immediately assigned a 
platform-specific role before their account is fully generated.
"""
class AdminUserCreationForm(UserCreationForm):
=======
# This is your 'Single Channel' logic from services.py
from .services import create_user_safely 

# --- 1. THE CUSTOM FORM ---
# This must be defined before CustomUserAdmin

class AdminUserCreationForm(UserCreationForm):
    """
    Custom form for the 'Add User' page in Django Admin.
    Adds the role dropdown to the initial account creation step.
    """
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "role")

<<<<<<< HEAD

"""
Instructs the Django Admin interface to display the Profile model fields directly 
beneath the Base User fields on the user detail page. This allows administrators 
to view and edit a user's core credentials and their extended contact and role 
information simultaneously without navigating to a separate table.
"""
=======
# --- 2. INLINES ---

>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0

<<<<<<< HEAD

"""
Instructs the Django Admin interface to display Photographer-specific fields alongside 
the Base User and Profile fields. It is utilized exclusively on the user edit page 
to allow administrators to manage a creator's public metadata, pricing, and experience 
seamlessly from one central location.
"""
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
class PhotographerInline(admin.StackedInline):
    model = Photographer
    can_delete = False
    extra = 0

<<<<<<< HEAD

"""
Replaces the default Django BaseUserAdmin to integrate platform-specific user management. 
It incorporates the custom creation form and inline models, altering the main admin 
list view to display the user's role. It intentionally intercepts the standard save 
operation to guarantee that the Base User, Profile, and Photographer records are 
generated reliably in a unified transaction when created by staff.
"""
class CustomUserAdmin(BaseUserAdmin):
=======
# --- 3. CUSTOM USER ADMIN ---

class CustomUserAdmin(BaseUserAdmin):
    # Use our custom form when clicking 'Add User'
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
    add_form = AdminUserCreationForm
    
    inlines = (ProfileInline, PhotographerInline)
    list_display = ('username', 'email', 'get_role', 'is_staff')
    
<<<<<<< HEAD
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
=======
    # This defines the layout specifically for the 'Add User' page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # CHANGED: password -> password1, password_confirmation -> password2
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )

<<<<<<< HEAD
    """
    A helper method used strictly within the CustomUserAdmin list view to safely fetch 
    and display the associated role from a user's linked Profile. If the profile is 
    missing or an unexpected error occurs during the database lookup, it gracefully 
    defaults to displaying "No Role".
    """
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
    def get_role(self, instance):
        try:
            return instance.profile.role
        except Exception:
            return "No Role"
    get_role.short_description = 'Role'

<<<<<<< HEAD
    """
    Overrides the default model saving behavior in the admin interface. When a brand 
    new user is being submitted by an administrator, it extracts the selected role and 
    delegates the actual database transaction to the imported `create_user_safely` 
    service, preventing incomplete profile generation or missing relations.
    """
    def save_model(self, request, obj, form, change):
        if not change:
            selected_role = form.cleaned_data.get('role', 'client')
            
=======
    def save_model(self, request, obj, form, change):
        if not change:  # This triggers ONLY when creating a NEW user
            # 1. Capture the role selected in the Admin dropdown (e.g., 'developer')
            selected_role = form.cleaned_data.get('role', 'client')
            
            # 2. Pass it to the Single Channel service
            # This service ensures the Profile role = selected_role
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
            user, created = create_user_safely(
                username=obj.username,
                password=obj.password, # Django Admin hashes this before save_model
                email=obj.email,
                role=selected_role
            )
            
<<<<<<< HEAD
            obj.pk = user.pk
        else:
            super().save_model(request, obj, form, change)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


"""
Configures the dedicated administrative page for the Profile model. It dictates 
which fields are displayed in the main table, enables sidebar filtering by user role, 
and provides a search bar to quickly locate specific user profiles by their exact 
username or phone number.
"""
=======
            # 3. Attach the ID to the admin object so the page doesn't crash
            obj.pk = user.pk
        else:
            # For existing users, just save the changes as normal
            super().save_model(request, obj, form, change)

# Re-register User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- 4. OTHER MODEL REGISTRATIONS ---

>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'address')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone')

<<<<<<< HEAD

"""
Configures the backend management view for the Photographer model. It organizes 
the display grid to show professional metrics like experience years and hourly rates 
at a glance, while enabling administrators to search the directory directly by 
the creator's username or their specified geographic location.
"""
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'price_per_hour', 'location')
    search_fields = ('user__username', 'location')

<<<<<<< HEAD

"""
Customizes the backend management of uploaded portfolio images. It configures the 
list view to display the owning photographer alongside the exact upload timestamp. 
It intentionally makes the upload date read-only to preserve data integrity and 
uses a custom method to check the status of the file attachment.
"""
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('photographer', 'uploaded_at', 'preview_image')
    readonly_fields = ('uploaded_at',)

<<<<<<< HEAD
    """
    A lightweight evaluation method utilized by the Portfolio list view to check 
    for the physical presence of an image file. It returns a simple text-based 
    status string instead of attempting to render the raw system file path to the administrator.
    """
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
    def preview_image(self, obj):
        if obj.image:
            return "Image Uploaded"
        return "No Image"

<<<<<<< HEAD

"""
Manages the backend interface for auditing all platform reservations. It structures 
the primary list view to show the client, the hired photographer, and the current 
job status. It also implements high-level administrative tools like date-based 
hierarchies and status filters to easily track the platform's booking lifecycle.
"""
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'photographer', 'event_date', 'status', 'created_at')
    list_filter = ('status', 'event_date')
    search_fields = ('client__username', 'photographer__user__username')
    date_hierarchy = 'event_date'

<<<<<<< HEAD

"""
Sets up the administrative oversight view for post-job client reviews. It displays 
the associated booking reference, the numeric rating score, and the submission date. 
It offers sidebar filtering by the rating value to help administrators quickly 
identify highly-rated creators or audit potential service disputes.
"""
=======
>>>>>>> c9a0b83914e7670bca034a88e89d4a92ed5ff58f
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('booking__photographer__user__username',)