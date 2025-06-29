import os
import json
import re
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpRequest

def navigation_page(request:HttpRequest):
    song_list = []
    data_dir = os.path.join(settings.BASE_DIR, "../crawler/Data/Song")

    if not os.path.exists(data_dir):
        raise Http404(data_dir)

    if os.path.exists(data_dir):
        for filename in os.listdir(data_dir):
            if filename.endswith(".json"):
                with open(os.path.join(data_dir, filename), "r", encoding="utf-8") as f:
                    data = json.load(f)
                    song_list.append({
                        "id": data.get("song_id", re.search(r"song_info_id=(.*?).json", filename).group(1)),
                        "name": data.get("song_name", "Unknown"),
                        "lyric": data.get("song_lyric", ""),
                        "comments": data.get("song_comments")
                    })
    
    context = {
        "song_list": song_list
    }

    return render(request, "navigation_page/navigation_page.html", context)