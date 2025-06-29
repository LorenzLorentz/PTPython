from django.urls import path
from . import views

urlpatterns = [
    path('<str:song_id>/', views.song_page, name="song_page"),
]