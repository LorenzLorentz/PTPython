from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Song, Singer
import random
from django.db.models import QuerySet

def get_song_list_random(num:int):
    all_song_ids = list(Song.objects.values_list("id", flat=True))
    random_song_ids = random.sample(all_song_ids, min(len(all_song_ids), num))
    song_list_random = Song.objects.filter(id__in=random_song_ids)
    return song_list_random

def get_singer_list_random(num:int):
    all_singer_ids = list(Singer.objects.values_list('id', flat=True))
    random_singer_ids = random.sample(all_singer_ids, min(len(all_singer_ids), num))
    singer_list_random = Singer.objects.filter(id__in=random_singer_ids)
    return singer_list_random

def get_song_list_same(singer_id:str, song_id:str=None, num:int=1):
    try:
        singer = get_object_or_404(Singer, singer_id=singer_id)
        if song_id:
            all_songs = singer.songs.exclude(id=song_id)
        else:
            all_songs = singer.songs
        all_song_ids = list(all_songs.values_list("id", flat=True))
        random_song_ids = random.sample(all_song_ids, min(len(all_song_ids), num))
        song_list_same = all_songs.filter(id__in=random_song_ids)
        return song_list_same
    except Exception as e:
        print(e)

def get_song_list_all():
    return Song.objects.all()

def get_singer_list_all():
    return Singer.objects.all()

def search_singer(query_singer: str) -> QuerySet[Singer]:
    return Singer.objects.filter(name__icontains=query_singer)

def search_song(query_song: str) -> QuerySet[Song]:
    return Song.objects.filter(name__icontains=query_song)