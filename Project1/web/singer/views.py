from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest
from django.core.paginator import Paginator
from data.views import get_singer_list_random, get_song_list_same
from data.models import Singer

def singer_page(request:HttpRequest, singer_id:str):
    """歌手详情界面"""

    # 获取歌手对象
    singer = get_object_or_404(Singer, singer_id=singer_id)
    
    # 获取下方分页显示歌曲
    song_list = singer.songs.all()
    paginator = Paginator(song_list, 10)
    song_list_page = paginator.get_page(request.GET.get('page'))
    
    # 获取右侧随机推荐歌曲
    song_list_same = get_song_list_same(singer.singer_id, num=3)

    # 获取右侧随机推荐歌手
    singer_list_random = get_singer_list_random(num=2)

    # 上下文数据
    context = {
        "singer": singer,
        "song_list_page": song_list_page,
        "song_list_same": song_list_same,
        "singer_list_random": singer_list_random,
    }
    
    # 渲染并返回Http响应
    return render(request, "singer_page/singer_page.html", context)