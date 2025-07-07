from django.conf import settings
from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from data.views import get_singer_list_all

def all_singers_page(request:HttpRequest):
    """所有歌手界面"""

    # 获取所有歌手, 并根据页码返回数据
    singer_list = get_singer_list_all()
    paginator = Paginator(singer_list, 12)
    singer_list_page = paginator.get_page(request.GET.get('page'))

    # 上下文数据
    context = {
        "singer_list_page": singer_list_page,
    }
    
    # 渲染并返回HTTP响应
    return render(request, "all_singers_page/all_singers_page.html", context)