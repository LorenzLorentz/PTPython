from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from data.views import get_song_list_all

def all_songs_page(request:HttpRequest):
    """所有歌曲界面"""

    # 获取所有歌曲, 并根据页码返回数据
    song_list = get_song_list_all()
    paginator = Paginator(song_list, 20)
    song_list_page = paginator.get_page(request.GET.get('page'))

    # 上下文数据
    context = {
        "song_list_page": song_list_page,
    }
    
    # 渲染并返回HTTP响应
    return render(request, "all_songs_page/all_songs_page.html", context)