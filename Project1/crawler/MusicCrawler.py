import json
import dataclasses
import requests

@dataclasses.dataclass
class SongInfo:
    """歌曲信息"""

    song_id: str
    song_name: str
    song_singer: tuple[str, str]
    song_album: str
    song_cover: str
    song_outer: str
    song_lyric: str
    song_url: str
    song_comments: list[dict]
    song_time: str

    def to_json(self) -> str:
        """转换为json文本"""
        data = dataclasses.asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=4)

    def save(self):
        """保存json和图片"""
        with open(f"Data/Song/song_info_id={self.song_id}.json", "w") as f:
            print(self.to_json(), file=f)

        with open(f"Data/Song/Image/{self.song_id}.jpg", "wb") as f:
            f.write(requests.get(url=self.song_cover).content)

@dataclasses.dataclass
class SingerInfo:
    """歌手信息"""

    singer_id: str
    singer_name: str
    singer_image: str
    singer_profile: str
    singer_url: str
    singer_songs: list[tuple[str, str]]

    def to_json(self) -> str:
        """转换为json文本"""

        data = dataclasses.asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=4)

    def save(self, file_path=None):
        """保存json和图片"""

        # 指定文件路径的保存方式
        if file_path:
            with open(file_path + f"/singer_info_id={self.singer_id}.json", "w") as f:
                print(self.to_json(), file=f)

            with open(file_path + f"/Image/{self.singer_id}.jpg", "wb") as f:
                f.write(requests.get(url=self.singer_image).content)
            
            return

        # 默认保存方式
        with open(f"Data/Singer/singer_info_id={self.singer_id}.json", "w") as f:
            print(self.to_json(), file=f)

        with open(f"Data/Singer/Image/{self.singer_id}.jpg", "wb") as f:
            f.write(requests.get(url=self.singer_image).content)

class MusicCrawler:
    """音乐爬虫基类, 定义了接口与需要实现的函数"""

    def __init__(self):
        # 初始化缓存
        self.song_detail_cache = {}
        self.singer_page_cache = {}

    def get_song_info(self, song_id:str) -> SongInfo:
        """调用接口, 爬取歌手信息"""

        song_name = self.get_song_name(song_id)
        song_singer = self.get_song_singer(song_id)
        song_album = self.get_song_album(song_id)
        song_cover = self.get_song_cover(song_id)
        song_outer = self.get_song_outer(song_id)
        song_lyric = self.get_song_lyric(song_id)
        song_url = self.get_song_url(song_id)
        song_comments = self.get_song_comments(song_id)
        song_time = self.get_song_time(song_id)
        self.song_detail_cache.pop(song_id)
        return SongInfo(song_id=song_id, song_name=song_name, song_singer=song_singer, song_album=song_album, song_cover=song_cover, song_outer=song_outer, song_lyric=song_lyric, song_url=song_url, song_comments=song_comments, song_time=song_time)
    
    def get_singer_info(self, singer_id:str) -> SingerInfo:
        """调用接口, 爬去歌曲信息"""

        singer_name = self.get_singer_name(singer_id)
        singer_image = self.get_singer_image(singer_id)
        singer_profile = self.get_singer_profile(singer_id)
        singer_url = self.get_singer_url(singer_id)
        singer_songs = self.get_singer_songs(singer_id)
        self.singer_page_cache.pop(singer_id)
        return SingerInfo(singer_id=singer_id, singer_name=singer_name, singer_image=singer_image, singer_profile=singer_profile, singer_url=singer_url, singer_songs=singer_songs)

    def get_song_name(self, song_id:str) -> str:
        """获得歌曲名字"""
        raise NotImplementedError()
    
    def get_song_album(self, song_id:str) -> str:
        """获得专辑名字"""
        raise NotImplementedError()

    def get_song_cover(self, song_id:str) -> str:
        """获得专辑封面url"""
        raise NotImplementedError()

    def get_song_singer(self, song_id:str) -> tuple[str, str]:
        """获得歌手id和姓名"""
        raise NotImplementedError()
    
    def get_song_outer(self, song_id:str) -> str:
        """获得歌曲播放器链接"""
        raise NotImplementedError()

    def get_song_lyric(self, song_id:str) -> str:
        """获得歌曲歌词"""
        raise NotImplementedError()

    def get_song_url(self, song_id:str) -> str:
        """获得歌曲原始链接"""
        raise NotImplementedError()

    def get_song_comments(self, song_id:str) -> list[dict]:
        """获得歌曲评论"""
        raise NotImplementedError()
    
    def get_song_time(self, song_id:str) -> str:
        """获得专辑发行时间"""
        raise NotImplementedError()

    def get_singer_name(self, song_id:str) -> str:
        """获得歌手姓名"""
        raise NotImplementedError()

    def get_singer_image(self, singer_id:str) -> str:
        """获得歌手照片url"""
        raise NotImplementedError()

    def get_singer_profile(self, singer_id:str) -> str:
        """获得歌手简介"""
        raise NotImplementedError()

    def get_singer_url(self, singer_id:str) -> str:
        """获得歌手原始链接"""
        raise NotImplementedError()
    
    def get_singer_songs(self, singer_id:str) -> list[str]:
        """获得歌手热门歌曲"""
        raise NotImplementedError()
    
    def get_all_singers(self):
        """获得歌手列表"""
        raise NotImplementedError()