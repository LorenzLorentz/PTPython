import os
import json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpRequest
from django.core.paginator import Paginator
from datetime import datetime
import random
from data.views import get_song_list_random, get_song_list_same
from data.models import Song, Comment
from django.views.decorators.http import require_POST

@require_POST
def delete_comment(request:HttpRequest, song_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    comment.delete()
    return redirect('song_page', song_id=song_id)

@require_POST
def add_comment(request:HttpRequest, song_id):
    nickname = request.POST.get("nickname", default="Anonymous")
    image = request.POST.get("image")
    content = request.POST.get("content")

    if content:
        Comment.objects.create(
            nickname=nickname,
            content=content,
            image=image,
            song=get_object_or_404(Song, song_id=song_id),
        )

    return redirect("song_page", song_id=song_id)

def song_page(request:HttpRequest, song_id:str):
    song = get_object_or_404(Song, song_id=song_id)

    # 1. 下方分页显示评论
    comment_list = song.comments.all()
    paginator = Paginator(comment_list, 10)
    comment_list_page = paginator.get_page(request.GET.get('page'))

    # 2. 右侧同一歌手的随机推荐歌曲
    song_list_same = get_song_list_same(singer_id=song.singer.singer_id,song_id=song.song_id, num=3)
    
    # 3. 右侧随机推荐歌曲
    song_list_random = get_song_list_random(num=2)

    context = {
        "song": song,
        "comment_list_page": comment_list_page,
        "song_list_same": song_list_same,
        "song_list_random": song_list_random
    }
    
    return render(request, "song_page/song_page.html", context)