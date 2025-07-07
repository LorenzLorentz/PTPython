from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from data.views import search_singer, search_song
import time

def search_page(request:HttpRequest):
    """搜索界面"""

    # 开始计时
    start_time = time.perf_counter()
    
    # 获取搜索信息
    search_type = request.GET.get("type")
    query = request.GET.get("q", "")[:20]
    page_number = request.GET.get('page')

    # 构建初始上下文
    context = {
        "query": query,
        "type": search_type,
    }

    # 根据具体搜索类型获得数据与上下文信息
    if search_type == "song":
        results = search_song(query_song=query)
        template = "search_page/search_page_song.html"
        context_key = "song_list_page"
    elif search_type == "singer":
        results = search_singer(query_singer=query)
        template = "search_page/search_page_singer.html"
        context_key = "singer_list_page"  
    else:
        raise NotImplementedError()

    # 根据分页信息获取数据
    paginator = Paginator(results, 12)
    page_obj = paginator.get_page(page_number)
    context[context_key] = page_obj
    context["num"] = len(results)

    # 终止计时
    context["time"] = f"{(time.perf_counter() - start_time):.3g}"

    return render(request, template, context)