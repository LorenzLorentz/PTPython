from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_songs_page, name="all_songs_page"),
]