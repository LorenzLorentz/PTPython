"""
URL configuration for music_web project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('song/', include('song.urls')),
    path('singer/', include('singer.urls')),
    path('all_songs/', include('all_songs.urls')),
    path('all_singers/', include('all_singers.urls')),
    path('search', include('search.urls')),
    # path('search/', include('search.urls')),
    path('', include('navigation.urls')),
]