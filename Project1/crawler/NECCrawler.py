import base64
import requests
import json
import re
from MusicCrawler import MusicCrawler
from encrypt import encrypt

class NECCrawler(MusicCrawler):
    def __init__(self, cookie:str):
        super().__init__()
        self.cookie = cookie
        self.csrf_token = re.search(r'__csrf=(.*?);', cookie).group(1)
        self.base_url = "https://music.163.com"
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
            "Referer": "https://music.163.com/",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _get_song_data(self, url:str, payload:dict) -> json:
        encrypted_data = encrypt(payload)
        res = requests.post(url, data=encrypted_data, headers=self.headers)
        # res.raise_for_status()
        return res.json()

    def get_song_detail(self, song_id:str):
        if not song_id in self.song_detail_cache.keys():
            url = f"{self.base_url}/weapi/song/detail"
            payload = {
                "id": song_id,
                "ids": f"[{song_id}]",
                "limit": 10000,
                "offset": 0,
                "csrf_token": self.csrf_token,
            }
            self.song_detail_cache.setdefault(song_id, self._get_song_data(url=url, payload=payload))
        return self.song_detail_cache[song_id]

    def get_song_name(self, song_id:str) -> str:
        return self.get_song_detail(song_id=song_id)["songs"][0]["name"]

    def get_song_singer(self, song_id:str) -> tuple[str, str]:
        temp = self.get_song_detail(song_id=song_id)["songs"][0]["artists"][0]
        return str(temp["id"]), temp["name"]

    def get_song_cover(self, song_id:str) -> str:
        return self.get_song_detail(song_id=song_id)["songs"][0]["album"]["picUrl"]

    def get_song_lyric(self, song_id:str) -> str:
        url = f"{self.base_url}/weapi/song/lyric?csrf_token={self.csrf_token}"
        payload = {
            "id": song_id,
            "lv": 0,
            "tv": 0,
            "csrf_token": self.csrf_token,
        }
        raw_lyric = self._get_song_data(url=url, payload=payload)["lrc"]["lyric"]
        return re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]\s*', '', raw_lyric)

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
        raw_comments = self._get_song_data(url=url, payload=payload)["data"]["comments"]
        comments = [{
            "nickname": item["user"]["nickname"],
            "image": item["user"]["avatarUrl"],
            "content": item["content"],
            "time": item["timeStr"]
        } for item in raw_comments]
        return json.dumps(comments, ensure_ascii=False)

    def _get_singer_data(self, singer_id:str) -> str:
        if not singer_id in self.singer_page_cache.keys():
            url = f"https://music.163.com/artist?id={singer_id}"
            self.singer_page_cache.setdefault(singer_id, requests.get(url=url, headers=self.headers).text)        
        return self.singer_page_cache[singer_id]
    
    def get_singer_name(self, singer_id:str) -> str:
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<meta name="keywords" content="(.*?)" />'
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)
        return None

    def get_singer_image(self, singer_id:str) -> str:
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<meta property="og:image" content="(.*?)"'
        match = re.search(pattern, html_content)
        
        if match:
            return match.group(1)
        return None

    def get_singer_profile(self, singer_id:str) -> str:
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<meta name="description" content="(.*?)" />'
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)
        return None

    def get_singer_url(self, singer_id:str) -> str:
        url = f"https://music.163.com/#/artist?id={singer_id}"
        return url
    
    def get_singer_songs(self, singer_id:str) -> list[tuple[str, str]]:
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<li><a href="/song\?id=(\d+)">(.*?)</a></li>'
        songs = re.findall(pattern, html_content)
        return songs