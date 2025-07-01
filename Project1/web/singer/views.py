import os
import json
import random
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import Http404, HttpRequest
from django.core.paginator import Paginator
from data.views import get_singer_list_random, get_song_list_same
from data.models import Singer

def singer_page(request:HttpRequest, singer_id:str):
    singer = get_object_or_404(Singer, singer_id=singer_id)
    
    # 1. 下方分页显示歌曲
    song_list = singer.songs.all()
    paginator = Paginator(song_list, 10)
    song_list_page = paginator.get_page(request.GET.get('page'))
    
    # 2. 右侧随机推荐歌曲
    # song_list_random = random.sample(song_list, k=min(3, len(singer["singer_songs"])))
    # get_song_info_from_id(song_list=song_list_random)
    song_list_same = get_song_list_same(singer.singer_id, num=3)

    # 3. 右侧随机推荐歌手
    singer_list_random = get_singer_list_random(num=2)

    context = {
        "singer": singer,
        "song_list_page": song_list_page,
        "song_list_same": song_list_same,
        "singer_list_random": singer_list_random,
    }
    
    return render(request, "singer_page/singer_page.html", context)