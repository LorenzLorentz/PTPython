import os
import json
import re
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpRequest
from django.core.paginator import Paginator
from data.views import get_song_list_all

def all_songs_page(request:HttpRequest):
    song_list = get_song_list_all()
    paginator = Paginator(song_list, 20)
    song_list_page = paginator.get_page(request.GET.get('page'))

    context = {
        "song_list_page": song_list_page,
    }
    
    return render(request, "all_songs_page/all_songs_page.html", context)