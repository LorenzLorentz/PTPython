from django.urls import path
from . import views

urlpatterns = [
    path('<str:song_id>/', views.song_page, name="song_page"),
    path('song/<str:song_id>/comment/<int:comment_id>/delete/', views.delete_comment, name="delete_comment"),
    path('song/<str:song_id>/comment/add/', views.add_comment, name="add_comment"),
]