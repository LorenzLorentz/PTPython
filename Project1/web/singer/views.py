import os
import json
import random
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest
from datetime import datetime

def singer_page(request:HttpRequest, singer_id:str):
    json_path = os.path.join(settings.BASE_DIR, "../crawler/Data/Singer", f"singer_info_id={singer_id}.json")

    if not os.path.exists(json_path):
        raise Http404(json_path)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    song_list = random.sample(data["singer_songs"], k=min(3, len(data["singer_songs"])))
    for i in range(len(song_list)):
        json_path = os.path.join(settings.BASE_DIR, "../crawler/Data/Song", f"song_info_id={song_list[i][0]}.json")
        
        temp_dict = {}
        if os.path.exists(json_path):
            with open(json_path, "r+", encoding="utf-8") as f:
                temp_dict = json.load(f)
        else:
            temp_dict = {
                "song_id": song_list[i][0],
                "song_name": song_list[i][1],
                "song_cover": "https://via.placeholder.com/60/FFC0CB/000000?Text=封面"
            }
        
        song_list[i] = temp_dict
    
    from navigation.views import get_singer_list
    singer_list = get_singer_list(num=2)

    context = {
        "singer": data,
        "song_list": song_list,
        "singer_list": singer_list,
    }
    
    return render(request, "singer_page/singer_page.html", context)