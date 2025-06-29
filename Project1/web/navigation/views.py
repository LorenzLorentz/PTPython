import os
import json
import random
import re
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpRequest

def get_song_list(num:int):
    song_list = []
    song_data_dir = os.path.join(settings.BASE_DIR, "../crawler/Data/Song")
    
    if not os.path.exists(song_data_dir):
        raise Http404(song_data_dir)

    if os.path.exists(song_data_dir):
        all_song_files = [f for f in os.listdir(song_data_dir) if f.endswith(".json")]
        num_songs_to_sample = min(num, len(all_song_files))
        selected_song_files = random.sample(all_song_files, num_songs_to_sample)
        for filename in selected_song_files:
            with open(os.path.join(song_data_dir, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                song_list.append({
                    "song_id": data.get("song_id", re.search(r"song_info_id=(.*?).json", filename).group(1)),
                    "song_name": data.get("song_name", "Unknown"),
                    "song_lyric": data.get("song_lyric", ""),
                    "song_comments": data.get("song_comments"),
                    "song_singer": data.get("song_singer"),
                    "song_cover": data.get("song_cover"),
                })
    
    return song_list

def get_singer_list(num:int):
    singer_list = []
    singer_data_dir = os.path.join(settings.BASE_DIR, "../crawler/Data/Singer")
    
    if not os.path.exists(singer_data_dir):
        raise Http404(singer_data_dir)

    if os.path.exists(singer_data_dir):
        all_singer_files = [f for f in os.listdir(singer_data_dir) if f.endswith(".json")]
        num_singers_to_sample = min(num, len(all_singer_files))
        selected_singer_files = random.sample(all_singer_files, num_singers_to_sample)

        for filename in selected_singer_files:
            with open(os.path.join(singer_data_dir, filename), "r", encoding="utf-8") as f:
                data = json.load(f)
                singer_list.append({
                    "singer_id": data.get("singer_id", re.search(r"singer_info_id=(.*?).json", filename).group(1)),
                    "singer_name": data.get("singer_name", "Unknown"),
                    "singer_profile": data.get("singer_profile", ""),
                    "singer_songs": data.get("singer_songs"),
                    "singer_image": data.get("singer_image"),
                })
    return singer_list

def navigation_page(request:HttpRequest):
    song_list = get_song_list(num=6)
    singer_list = get_singer_list(num=4)
    
    context = {
        "song_list": song_list,
        "singer_list": singer_list
    }

    return render(request, "navigation_page/navigation_page.html", context)