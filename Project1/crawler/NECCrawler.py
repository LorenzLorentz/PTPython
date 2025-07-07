import csv
import requests
import json
import re
from MusicCrawler import MusicCrawler
from encrypt import encrypt
from datetime import datetime
import time
from bs4 import BeautifulSoup as bs

class NECCrawler(MusicCrawler):
    def __init__(self, cookie:str):
        super().__init__()

        """爬虫基础信息设置"""
        self.cookie = cookie
        # 根据cokkie解析csrf_token
        self.csrf_token = re.search(r'__csrf=(.*?)', cookie).group(1)
        self.base_url = "https://music.163.com"
        # 构建header
        self.headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0",
            "Referer": "https://music.163.com/",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    def _get_song_data(self, url:str, payload:dict) -> json:
        """根据url和payload构造请求, 获得数据"""
        
        # 重试参数设置
        max_retries = 10
        delay_seconds = 0.5
        
        # 加密原始payload, 获得参数和密钥
        encrypted_data = encrypt(payload)
        
        for attempt in range(max_retries):
            try:
                # 构造请求, 获得数据
                res = requests.post(url, data=encrypted_data, headers=self.headers, timeout=10)
                res.raise_for_status()
                res = res.json()

                if res["code"]==405:
                    raise requests.exceptions.RequestException

                return res

            # 错误重试处理
            except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                if attempt < max_retries - 1:
                    time.sleep(delay_seconds)
        
        raise ValueError("请求失败")

    def get_song_detail(self, song_id:str):
        """获取歌曲detail信息"""

        # 带缓存的请求逻辑
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
        """获得歌曲名字"""
        dic = self.get_song_detail(song_id=song_id)
        return dic["songs"][0]["name"]

    def get_song_singer(self, song_id:str) -> tuple[str, str]:
        """获得歌手id和姓名"""
        temp = self.get_song_detail(song_id=song_id)["songs"][0]["artists"][0]
        return str(temp["id"]), temp["name"]

    def get_song_album(self, song_id:str) -> str:
        """获得专辑名字"""
        return self.get_song_detail(song_id=song_id)["songs"][0]["album"]["name"]

    def get_song_cover(self, song_id:str) -> str:
        """获得专辑封面url"""
        return self.get_song_detail(song_id=song_id)["songs"][0]["album"]["picUrl"]
    
    def get_song_outer(self, song_id:str) -> str:
        """获得歌曲播放器链接"""
        return f"https://music.163.com/song/media/outer/url?id={song_id}.mp3"

    def get_song_lyric(self, song_id:str) -> str:
        """获得歌曲歌词"""
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
        """获得歌曲原始链接"""
        return f"https://music.163.com/#/song?id={song_id}"

    def get_song_comments(self, song_id:str) -> list[dict]:
        """获得歌曲评论"""
        url = f"https://music.163.com/weapi/comment/resource/comments/get?csrf_token={self.csrf_token}"
        payload = {
            "csrf_token": self.csrf_token,
            "cursor": "-1",
            "offset": "0",
            "ordertype": "1",
            "pageNo": "1",
            "pageSize": "20",
            "rid": f"R_SO_4_{song_id}",
            "threadId": f"R_SO_4_{song_id}",
		}
        
        # 获取热门评论和第一页评论
        raw_json = self._get_song_data(url=url, payload=payload)
        raw_comments = raw_json["data"]["comments"]
        if raw_json["data"]["hotComments"]:
            raw_comments = raw_json["data"]["hotComments"] + raw_comments
        
        # 解析原始json并保存所需数据
        comments = [{
            "nickname": item["user"]["nickname"],
            "image": item["user"]["avatarUrl"],
            "content": item["content"],
            "time": item["timeStr"]
        } for item in raw_comments]
        
        return json.dumps(comments, ensure_ascii=False)
    
    def get_song_time(self, song_id:str) -> int:
        """获得专辑发行时间"""
        time = self.get_song_detail(song_id=song_id)["songs"][0]["album"]["publishTime"]
        return datetime.fromtimestamp(time/1000).strftime('%Y-%m-%d')

    def _get_singer_data(self, singer_id:str) -> str:
        """获取歌手主页内容"""
        # 带缓存的请求逻辑
        if not singer_id in self.singer_page_cache.keys():
            url = f"https://music.163.com/artist?id={singer_id}"
            self.singer_page_cache.setdefault(singer_id, requests.get(url=url, headers=self.headers).text)        
        return self.singer_page_cache[singer_id]
    
    def get_singer_name(self, singer_id:str) -> str:
        """获得歌手姓名"""
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<meta name="keywords" content="(.*?)" />'
        match = re.search(pattern, html_content)
        if match:
            return match.group(1)
        return None

    def get_singer_image(self, singer_id:str) -> str:
        """获得歌手照片url"""
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<meta property="og:image" content="(.*?)"'
        match = re.search(pattern, html_content)
        
        if match:
            return match.group(1)
        return None

    def get_singer_profile(self, singer_id:str) -> str:
        """获得歌手简介"""
        html_content = self._get_singer_data(singer_id=singer_id)
        # 通过BeautifulSoup解析html文本
        soup = bs(html_content, 'html.parser')
        desc = soup.find('meta', attrs={'property': 'og:abstract'})
        if desc:
            return desc['content']
        return None

    def get_singer_url(self, singer_id:str) -> str:
        """获得歌手原始链接"""
        url = f"https://music.163.com/#/artist?id={singer_id}"
        return url
    
    def get_singer_songs(self, singer_id:str) -> list[tuple[str, str]]:
        """获得歌手热门歌曲"""
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<li><a href="/song\?id=(\d+)">(.*?)</a></li>'
        songs = re.findall(pattern, html_content)
        return songs
    
    def get_all_singers(self):
        """获得歌手列表"""

        # 华语歌手相关标签
        id_list = [1001, 1002, 1003]
        ini_list = [0, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90]
        
        for id in id_list:
            for ini in ini_list:
                # 获取请求
                url = f"http://music.163.com/discover/artist/cat?id={str(id)}&initial={str(ini)}"
                res = requests.get(url=url, headers=self.headers).text
                # 匹配所有歌手
                singers = re.findall(r'<a href=".*?/artist\?id=(\d+)" class="nm nm-icn f-thide s-fc0" title=".*?的音乐">(.*?)</a>', res, re.S)
                
                for singer in singers:
                    with open("Data/all_singers.csv", "a+", newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow((singer[0], singer[1]))