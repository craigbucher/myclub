"""myclub_website URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.conf import settings  # imports settings.py
from django.conf.urls.static import static  # imports static_url

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('events.urls')),
    # allows use of authentication system URLs
    path('members/', include('django.contrib.auth.urls')),
    path('members/', include('members.urls')),
    # when image/media is uploaded, will create reference URL to save in database,
    # since can't save actual image in the datatbase
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Configure Admin Titles
admin.site.site_header = 'My Club Administration Page'  # Top banner
admin.site.site_title = 'Browser Title'  # Browser tab
admin.site.index_title = 'Welcome To The Admin Area'

# Admin panel CSS is in virtual environment:
# lib/python3.10/site-packages/django/contrib/admin/static/admin/css/base.css
# *but* should make own base.css file in app and have it override this one
