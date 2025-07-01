import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from data.models import Singer, Song, Comment
from datetime import datetime

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS("Start Importing Data..."))

        base_dir = settings.BASE_DIR
        singer_dir = os.path.join(base_dir, "../crawler/Data", "Singer")
        song_dir = os.path.join(base_dir, "../crawler/Data", "Song")

        self.stdout.write("Loading Singer Data")
        singer_files = [f for f in os.listdir(singer_dir) if f.endswith('.json')]

        for singer_file in singer_files:
            with open(os.path.join(singer_dir, singer_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if data.get("singer_name") is None:
                    data["singer_name"] = "Unknown"
                
                try:
                    singer, created = Singer.objects.update_or_create(
                        singer_id = data.get("singer_id"),
                        defaults = {
                            "name": data.get("singer_name"),
                            "profile": data.get("singer_profile"),
                            "image": data.get("singer_image"),
                            "url": data.get("singer_url"),
                        }
                    )
                    
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Creating: {singer.name}"))
                    else:
                        self.stdout.write(f"Updating: {singer.name}")
                except Exception as e:
                    print(e)

        self.stdout.write("Loading Song Data")
        song_files = [f for f in os.listdir(song_dir) if f.endswith('.json')]

        for song_file in song_files:
            with open(os.path.join(song_dir, song_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                singer_name = data.get("song_singer")[1]

                try:
                    singer_obj = Singer.objects.get(name=singer_name)

                    song, created = Song.objects.update_or_create(
                        song_id = data.get("song_id"),
                        defaults = {
                            "name": data.get("song_name"),
                            "cover": data.get("song_cover"),
                            "lyric": data.get("song_lyric"),
                            "url": data.get("song_url"),
                            "singer": singer_obj
                        }
                    )
                    
                    if created:
                        comments_raw = data.get("song_comments")
                        if isinstance(comments_raw, str):
                            comments_raw = json.loads(comments_raw)

                        for comment_raw in comments_raw:
                            comment_time = comment_raw.get("time")
                            if comment_time:
                                comment_time = datetime.strptime(comment_time, "%Y-%m-%d")

                            comment, created = Comment.objects.update_or_create(
                                nickname = comment_raw.get("nickname"),
                                image = comment_raw.get("image"),
                                content = comment_raw.get("content"),
                                time = comment_time,
                                song = song
                            )

                        self.stdout.write(self.style.SUCCESS(f"Creating: {song.name}"))
                    else:
                        self.stdout.write(f"Updating: {song.name}")

                except Singer.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Warning: Song "{data.get("song_name")}" \'s singer "{singer_name}" does not exist'))
                except Exception as e:
                    break

        self.stdout.write(self.style.SUCCESS("Finished Importing Data"))
        print("singers", Singer.objects.count())
        print("songs", Song.objects.count())