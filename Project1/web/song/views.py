import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest
from datetime import datetime
import random

def get_song_list_same(singer_id:str, num:int):
    song_list_same = []
    
    json_path_singer = os.path.join(settings.BASE_DIR, "../crawler/Data/Singer", "singer_info_id={}.json".format(singer_id))
    if os.path.exists(json_path_singer):
        with open(json_path_singer, "r", encoding="utf-8") as f:
            singer = json.load(f)
        
        song_list_same = random.sample(singer["singer_songs"], k=min(num, len(singer["singer_songs"])))
        
        for i in range(len(song_list_same)):
            original_song_item = song_list_same[i]
            song_id = original_song_item[0]
            song_name = original_song_item[1]

            json_path = os.path.join(settings.BASE_DIR, "../crawler/Data/Song", f"song_info_id={song_id}.json")

            song_detail_dict = {}

            if os.path.exists(json_path):
                with open(json_path, "r", encoding="utf-8") as f:
                    song_detail_dict = json.load(f)
            else:
                song_detail_dict = {
                    "song_id": song_id,
                    "song_name": song_name,
                    "song_cover": "https://via.placeholder.com/60/FFC0CB/000000?Text=封面"
                }
            
            song_list_same[i] = song_detail_dict

    return song_list_same

def song_page(request:HttpRequest, song_id:str):
    json_path = os.path.join(settings.BASE_DIR, "../crawler/Data/Song", f"song_info_id={song_id}.json")

    if not os.path.exists(json_path):
        raise Http404(json_path)

    if request.method == 'POST':
        nickname = request.POST.get("nickname", default="Anonymous")
        image = request.POST.get("image")
        content = request.POST.get("content")

        if content:
            new_comment = {
                "nickname": nickname,
                "image": image,
                "content": content,
                "time": datetime.now().strftime("%Y-%m-%d"),
                "image": "https://via.placeholder.com/50/4CAF50/FFFFFF?Text=U",
            }

            with open(json_path, "r+", encoding="utf-8") as f:
                data = json.load(f)
                comments = json.loads(data["song_comments"])
                data["song_comments"] = comments
                comments.append(new_comment)
                f.seek(0)
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.truncate()

            return redirect("song_page", song_id=song_id)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data["song_comments"], str):
            data["song_comments"] = json.loads(data["song_comments"])

    song_list_same = get_song_list_same(singer_id=data["song_singer"][0], num=3)
    from navigation.views import get_song_list
    song_list_random = get_song_list(num=2)

    context = {
        "song": data,
        "song_list_same": song_list_same,
        "song_list_random": song_list_random
    }
    
    return render(request, "song_page/song_page.html", context)