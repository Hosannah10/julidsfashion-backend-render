from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')),
    path('api/', include('catalog.urls')),
    path("api/", include('contact.urls')),
    path('api/', include('orders.urls')),
    path('api/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
