from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm  # Required for the custom form
from django.contrib.auth.models import User

from .models import Profile, Photographer, Portfolio, Booking, Review
# This is your 'Single Channel' logic from services.py
from .services import create_user_safely 

# --- 1. THE CUSTOM FORM ---
# This must be defined before CustomUserAdmin

class AdminUserCreationForm(UserCreationForm):
    """
    Custom form for the 'Add User' page in Django Admin.
    Adds the role dropdown to the initial account creation step.
    """
    role = forms.ChoiceField(choices=Profile.ROLE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "role")

# --- 2. INLINES ---

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0

class PhotographerInline(admin.StackedInline):
    model = Photographer
    can_delete = False
    extra = 0

# --- 3. CUSTOM USER ADMIN ---

class CustomUserAdmin(BaseUserAdmin):
    # Use our custom form when clicking 'Add User'
    add_form = AdminUserCreationForm
    
    inlines = (ProfileInline, PhotographerInline)
    list_display = ('username', 'email', 'get_role', 'is_staff')
    
    # This defines the layout specifically for the 'Add User' page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # CHANGED: password -> password1, password_confirmation -> password2
            'fields': ('username', 'password1', 'password2', 'role'),
        }),
    )

    def get_role(self, instance):
        try:
            return instance.profile.role
        except Exception:
            return "No Role"
    get_role.short_description = 'Role'

    def save_model(self, request, obj, form, change):
        if not change:  # This triggers ONLY when creating a NEW user
            # 1. Capture the role selected in the Admin dropdown (e.g., 'developer')
            selected_role = form.cleaned_data.get('role', 'client')
            
            # 2. Pass it to the Single Channel service
            # This service ensures the Profile role = selected_role
            user, created = create_user_safely(
                username=obj.username,
                password=obj.password, # Django Admin hashes this before save_model
                email=obj.email,
                role=selected_role
            )
            
            # 3. Attach the ID to the admin object so the page doesn't crash
            obj.pk = user.pk
        else:
            # For existing users, just save the changes as normal
            super().save_model(request, obj, form, change)

# Re-register User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# --- 4. OTHER MODEL REGISTRATIONS ---

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone', 'address')
    list_filter = ('role',)
    search_fields = ('user__username', 'phone')

@admin.register(Photographer)
class PhotographerAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'price_per_hour', 'location')
    search_fields = ('user__username', 'location')

@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ('photographer', 'uploaded_at', 'preview_image')
    readonly_fields = ('uploaded_at',)

    def preview_image(self, obj):
        if obj.image:
            return "Image Uploaded"
        return "No Image"

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('client', 'photographer', 'event_date', 'status', 'created_at')
    list_filter = ('status', 'event_date')
    search_fields = ('client__username', 'photographer__user__username')
    date_hierarchy = 'event_date'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('booking__photographer__user__username',)