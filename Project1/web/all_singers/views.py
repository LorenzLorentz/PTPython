import os
import json
import re
from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpRequest
from django.core.paginator import Paginator
from data.views import get_singer_list_all

def all_singers_page(request:HttpRequest):
    singer_list = get_singer_list_all()
    paginator = Paginator(singer_list, 12)
    singer_list_page = paginator.get_page(request.GET.get('page'))

    context = {
        "singer_list_page": singer_list_page,
    }
    
    return render(request, "all_singers_page/all_singers_page.html", context)