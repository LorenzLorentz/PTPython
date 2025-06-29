from django.urls import path
from . import views

urlpatterns = [
    path('<str:singer_id>/', views.singer_page, name="singer_page"),
]