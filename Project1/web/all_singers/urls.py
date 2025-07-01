from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_singers_page, name="all_singers_page"),
]