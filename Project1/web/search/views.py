from django.shortcuts import render
from django.http import HttpRequest
from django.core.paginator import Paginator
from data.views import search_singer, search_song
import time

def search_page(request:HttpRequest):
    start_time = time.perf_counter()
    
    search_type = request.GET.get("type")
    query = request.GET.get("q", "")
    page_number = request.GET.get('page')

    context = {
        "query": query,
        "type": search_type,
    }

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

    paginator = Paginator(results, 12)
    page_obj = paginator.get_page(page_number)
    context[context_key] = page_obj
    context["num"] = len(results)
    context["time"] = f"{(time.perf_counter() - start_time):.3g}"

    return render(request, template, context)