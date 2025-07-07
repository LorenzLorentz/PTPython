import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from data.models import Singer, Song, Comment
from datetime import datetime, timedelta
from django.utils import timezone
from tqdm import tqdm

def split_name_and_alias(s:str):
    """分割名字与别名"""

    res = s.partition('，')
    return res[0].strip(), (res[1]+res[2]).strip() or None

def parse_time(time:str, default_year=None):
    """解析时间文本"""

    if not time or not isinstance(time, str):
        return None

    time = time.strip()
    now = timezone.now()

    if time.startswith("昨天"):
        try:
            yesterday_date = (now - timedelta(days=1)).date()
            time_str = time.replace("昨天", "").strip()
            if time_str:
                parsed_time = datetime.strptime(time_str, "%H:%M").time()
            else:
                parsed_time = datetime.min.time()
            naive_dt = datetime.combine(yesterday_date, parsed_time)
            return timezone.make_aware(naive_dt)
        except ValueError:
            pass

    if time.endswith("天前"):
        try:
            num_str = time.replace("天前", "").strip()
            to_sub = int(num_str)
            return now-timedelta(days=to_sub)
        except ValueError:
            pass

    possible_formats = ['%Y-%m-%d', '%m-%d']
    
    if default_year is None:
        default_year = datetime.now().year

    for fmt in possible_formats:
        try:
            dt = datetime.strptime(time, fmt)
            if "%Y" not in fmt:
                dt = dt.replace(year=default_year)
            return timezone.make_aware(dt)
        except (ValueError, TypeError):
            continue
    
    raise ValueError(f"Fail to parse! time={time}")

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        """将json文件导入数据库"""

        self.stdout.write(self.style.SUCCESS("Start Importing Data..."))

        # 相关文件夹设置
        base_dir = settings.BASE_DIR
        singer_dir = os.path.join(base_dir, "../crawler/Data", "Singer")
        song_dir = os.path.join(base_dir, "../crawler/Data", "Song")

        self.stdout.write("Loading Singer Data")
        singer_files = [f for f in os.listdir(singer_dir) if f.endswith('.json')]

        for singer_file in singer_files:
            """导入歌手"""
            with open(os.path.join(singer_dir, singer_file), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                if data.get("singer_name") is None:
                    data["singer_name"] = "Unknown"
                name, alias = split_name_and_alias(data["singer_name"])

                try:
                    # 创建歌手, 唯一性标准为singer_id
                    singer, created = Singer.objects.update_or_create(
                        singer_id = data.get("singer_id"),
                        defaults = {
                            "name": name,
                            "alias": alias,
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

        num_fail_song = 0
        with tqdm(song_files, desc="Processing Songs", leave=False) as pbar:
            for song_file in pbar:
                """导入歌曲"""
                with open(os.path.join(song_dir, song_file), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    singer_name = data.get("song_singer")[1]
                    singer_singer_id = data.get("song_singer")[0]

                    try:
                        # 获取对应歌手
                        singer_obj = Singer.objects.get(singer_id=singer_singer_id)

                        # 创建歌曲, 唯一性标准为song_id
                        song, created = Song.objects.update_or_create(
                            song_id = data.get("song_id"),
                            defaults = {
                                "name": data.get("song_name"),
                                "album": data.get("song_album"),
                                "cover": data.get("song_cover"),
                                "outer": data.get("song_outer"),
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
                                """导入评论"""
                                comment_time = comment_raw.get("time")
                                
                                # 解析评论时间
                                try:
                                    comment_time = parse_time(comment_time)
                                except Exception as e:
                                    print(e)
                                    num_fail_song += 1
                                    with open("error.log", "w") as f:
                                        print("comment", data.get("song_id"), e, file=f)
                                    continue
                                
                                # 创建评论
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

                    # 错误信息处理与记录
                    except Singer.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Warning: Song "{data.get("song_name")}" \'s singer "{singer_name}" does not exist'))
                        num_fail_song += 1
                    except Exception as e:
                        print(e)
                        num_fail_song += 1
                        with open("error.log", "w") as f:
                            print(data.get("song_id"), e, file=f)
                    pbar.set_postfix(fails=num_fail_song)

        self.stdout.write(self.style.SUCCESS("Finished Importing Data"))
        print("singers", Singer.objects.count())
        print("songs", Song.objects.count())