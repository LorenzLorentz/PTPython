from django.urls import path
from . import views

urlpatterns = [
    path("", views.navigation_page, name='navigation_page'),
]