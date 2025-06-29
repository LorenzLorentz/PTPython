import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404, HttpRequest
from datetime import datetime

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
                "time": datetime.now().strftime("%Y-%m-%d")
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
        data["song_comments"] = json.loads(data["song_comments"])
    
    return render(request, "song_page/song_page.html", {"song": data})