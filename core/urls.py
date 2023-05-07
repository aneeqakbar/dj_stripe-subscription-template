"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from core.utils import serve_static
import djstripe.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('authentication.urls')),
    path("stripe/", include("djstripe.urls", namespace="djstripe")),
    path("subscriptions/", include("subscriptions.urls")),
]

urlpatterns += serve_static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "ADMIN PANEL"
admin.site.site_title = "ADMIN PANEL"
admin.site.index_title = "Custom Title"
