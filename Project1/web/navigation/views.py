import os
import json
import random
import re
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpRequest
from data.views import get_singer_list_random, get_song_list_random

def navigation_page(request:HttpRequest):
    song_list = get_song_list_random(num=6)
    singer_list = get_singer_list_random(num=4)
    
    context = {
        "song_list": song_list,
        "singer_list": singer_list
    }

    return render(request, "navigation_page/navigation_page.html", context)