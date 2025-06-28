import base64
import json
import dataclasses

@dataclasses.dataclass
class SongInfo:
    song_id: str
    song_name: str
    song_singer: str
    song_cover: str
    song_lyric: str
    song_url: str
    song_comments: list[dict]

    def to_json(self) -> str:
        data = dataclasses.asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=4)

    def save(self):
        with open(f"song_info_id={self.song_id}.json", "w") as f:
            print(self.to_json(), file=f)

@dataclasses.dataclass
class SingerInfo:
    singer_id: str
    singer_name: str
    singer_image: str
    singer_profile: str
    singer_url: str
    singer_songs: list[str]

    def to_json(self) -> str:
        data = dataclasses.asdict(self)
        return json.dumps(data, ensure_ascii=False, indent=4)

    def save(self):
        with open(f"singer_info_id={self.singer_id}.json", "w") as f:
            print(self.to_json(), file=f)

class MusicCrawler:
    def __init__(self):
        self.song_detail_cache = {}
        self.singer_page_cache = {}

    def get_song_info(self, song_id:str) -> SongInfo:
        song_name = self.get_song_name(song_id)
        song_cover = self.get_song_cover(song_id)
        song_singer = self.get_song_singer(song_id)
        song_lyric = self.get_song_lyric(song_id)
        song_url = self.get_song_url(song_id)
        song_comments = self.get_song_comments(song_id)
        self.detail_cache.pop(song_id)
        return SongInfo(song_id=song_id, song_name=song_name, song_singer=song_singer, song_cover=song_cover ,song_lyric=song_lyric, song_url=song_url, song_comments=song_comments)
    
    def get_singer_info(self, singer_id:str) -> SingerInfo:
        singer_name = self.get_singer_name(singer_id)
        singer_image = self.get_singer_image(singer_id)
        singer_profile = self.get_singer_profile(singer_id)
        singer_url = self.get_singer_url(singer_id)
        singer_songs = self.get_singer_songs(singer_id)
        
        return SingerInfo(singer_id=singer_id, singer_name=singer_name, singer_image=singer_image, singer_profile=singer_profile, singer_url=singer_url, singer_songs=singer_songs)

    def get_song_name(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_song_cover(self, song_id:str) -> base64:
        raise NotImplementedError()

    def get_song_singer(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_song_lyric(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_song_url(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_song_comments(self, song_id:str) -> list[dict]:
        raise NotImplementedError()

    def get_singer_name(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_singer_image(self, singer_id:str) -> str:
        raise NotImplementedError()

    def get_singer_profile(self, singer_id:str) -> str:
        raise NotImplementedError()

    def get_singer_url(self, singer_id:str) -> str:
        raise NotImplementedError()
    
    def get_singer_songs(self, singer_id:str) -> list[str]:
        raise NotImplementedError()