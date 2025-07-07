from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest
from data.views import get_singer_list_random, get_song_list_random

def navigation_page(request:HttpRequest):
    """主页, 导航界面"""

    # 获取随机推荐歌手和歌曲
    song_list = get_song_list_random(num=6)
    singer_list = get_singer_list_random(num=4)
    
    # 上下文数据
    context = {
        "song_list": song_list,
        "singer_list": singer_list
    }

    # 渲染并返回Http响应
    return render(request, "navigation_page/navigation_page.html", context)