from django.db import models

class Singer(models.Model):
    """歌手数据模型"""

    singer_id = models.CharField(max_length=10, unique=True, verbose_name="singer_id")
    name = models.CharField(max_length=100, unique=True, verbose_name="singer_name")
    alias = models.CharField(max_length=200, verbose_name="singer_alias", blank=True, null=True)
    profile = models.TextField(blank=True, null=True, verbose_name="singer_profile")
    image = models.URLField(max_length=255, blank=True, null=True, verbose_name="singer_image_url")
    url = models.URLField(max_length=255, blank=True, null=True, verbose_name="singer_url")

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        verbose_name = "singer"
        verbose_name_plural = verbose_name

class Song(models.Model):
    """歌曲数据模型"""

    song_id = models.CharField(max_length=10, unique=True, verbose_name="song_id")
    name = models.CharField(max_length=200, verbose_name="song_name")
    album = models.CharField(max_length=200, verbose_name="song_album")
    cover = models.URLField(max_length=255, verbose_name="song_cover")
    outer = models.URLField(max_length=255, blank=True, null=True, verbose_name="song_outer")
    lyric = models.TextField(blank=True, null=True, verbose_name="song_lyric")
    url = models.URLField(max_length=255, blank=True, null=True, verbose_name="song_url")

    # 链接对应Singer
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE, related_name='songs', verbose_name="singer")

    def __str__(self):
        return f"{self.id} - {self.name} - {self.singer.name}"

    class Meta:
        verbose_name = "song"
        verbose_name_plural = verbose_name

class Comment(models.Model):
    """评论数据模型"""

    nickname = models.CharField(max_length=50, verbose_name="nickname")
    image = models.URLField(max_length=255, blank=True, null=True, verbose_name="image")
    content = models.TextField(verbose_name="content")
    time = models.DateTimeField(null=True, blank=True, verbose_name="time")

    # 链接对应Song
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name="comments", verbose_name="song")

    def __str__(self):
        return f'{self.nickname}: {self.content[:20]}'

    class Meta:
        verbose_name = "comment"
        verbose_name_plural = verbose_name
        ordering = ["time"]