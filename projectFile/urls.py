<<<<<<< HEAD
"""
URL configuration for projectFile project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.cache import never_cache

# --- NEW: Import your custom 403 view ---
# If you put the view in accounts/views.py, change 'core' to 'accounts'
from accounts.views import custom_403_view 
# ----------------------------------------

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('features/', include('features.urls')),
    # If your login/register paths are in a separate accounts app, 
    # you might also need this line if you haven't added it yet:
    # path('accounts/', include('accounts.urls')), 
]

# --- NEW: Register the 403 handler ---
handler403 = custom_403_view
# -------------------------------------

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
=======
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('features/', include('features.urls')),
]
>>>>>>> fa2185a29b4a06bc566f661b75273322ac13dc09
