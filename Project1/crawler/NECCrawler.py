import base64
import requests
from MusicCrawler import MusicCrawler, SongInfo, SingerInfo
from encrypt import encrypt

class NECCrawler(MusicCrawler):
    def __init__(self, csrf_token:str):
        self.csrf_token = csrf_token
        self.base_url = "https://music.163.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
            "Referer": "https://music.163.com/",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _get_song_data(self, url:str, payload:dict):
        encrypted_data = encrypt(payload)
        res = requests.post(url, data=encrypted_data, headers=self.headers)
        # res.raise_for_status()
        return res.json()

    def get_song_detail(self, song_id:str):
        url = f"{self.base_url}/weapi/song/detail"
        payload = {
            "id": song_id,
            "ids": f"[{song_id}]",
            "limit": 10000,
            "offset": 0,
            "csrf_token": self.csrf_token,
		}
        return  self._get_song_data(url=url, payload=payload)

    def get_song_name(self, song_id:str) -> str:
        raise NotImplementedError()

    def get_song_cover(self, song_id:str) -> base64:
        raise NotImplementedError()

    def get_song_lyric(self, song_id:str) -> str:
        url = f"{self.base_url}/weapi/song/lyric?csrf_token={self.csrf_token}"
        payload = {
            "id": song_id,
            "lv": 0,
            "tv": 0,
            "csrf_token": self.csrf_token,
        }
        return self._get_song_data(url=url, payload=payload)

    def get_song_url(self, song_id:str) -> str:
        return f"https://music.163.com/#/song?id={song_id}"

    def get_song_comments(self, song_id:str) -> list[dict]:
        url = f"https://music.163.com/weapi/comment/resource/comments/get?csrf_token={self.csrf_token}"
        payload = {
            "csrf_token": self.csrf_token,
            "cursor": "-1",
            "offset": "0",
            "ordertype": "1",
            "pageNo": "1",
            "pageSize": "20",
            "rid": "R_SO_4_212233",
            "threadId": "R_SO_4_212233",
		}
        return  self._get_song_data(url=url, payload=payload)
    
    def get_song_search(self, s=''):
        url = f'https://music.163.com/weapi/cloudsearch/get/web?csrf_token={self.csrf_token}'
        payload = {
            "hlpretag": "<span class=\"s-fc7\">",
            "hlposttag": "</span>",
            "s": s,
            "type": 1,
            "offset": 0,
            "total": "true",
            "limit": 30,
            "csrf_token": self.csrf_token
        }
        return self._get_song_data(url=url, payload=payload)

if __name__ == "__main__":
    c = NECCrawler(csrf_token="1db06a312a7d023e241d12a38384910c")
    print(c.get_song_detail(song_id="333750"))
    print(c.get_song_lyric(song_id="333750"))
    print(c.get_song_comments(song_id="333750"))