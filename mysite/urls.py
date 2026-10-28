"""
URL configuration for mysite project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.contrib import admin           # new add
from django.urls import path, include        # new add
from xml.dom.minidom import Document        # new add
from django.conf import settings             # new add
from django.conf.urls.static import static    # new add

urlpatterns = [
    path('admin/', admin.site.urls),          # new add
    path('', include('home.urls')),  
   


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
