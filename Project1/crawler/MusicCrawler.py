import base64
import dataclasses

@dataclasses.dataclass
class SongInfo:
    song_id: str
    song_name: str
    song_cover: str
    song_lyric: str
    song_url: str
    song_comments: list[dict]

@dataclasses.dataclass
class SingerInfo:
    singer_id: str
    singer_name: str
    singer_image: str
    singer_profile: str
    singer_url: str

class MusicCrawler:
    def __init__(self):
        pass

    def get_music_info(self, song_id:str):
        song_name = self.get_song_name(song_id)
        song_cover = self.get_song_cover(song_id)
        song_lyric = self.get_song_lyric(song_id)
        song_url = self.get_song_url(song_id)
        song_comments = self.get_song_comments(song_id)

        return SongInfo(song_id, song_name, song_cover, song_lyric, song_url, song_comments)
    
    def get_singer_info(self, singer_id:str):
        singer_name = self.get_singer_name(singer_id)
        singer_image = self.get_singer_name(singer_id)
        singer_profile = self.get_singer_profile(singer_id)
        singer_url = self.get_singer_url(singer_id)
        
        return SingerInfo(singer_id, singer_name, singer_image, singer_profile, singer_url)

    def get_song_name(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_song_cover(self, song_id:str) -> base64:
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