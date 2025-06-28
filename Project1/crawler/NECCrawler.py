import base64
import requests
import json
import re
from MusicCrawler import MusicCrawler, SongInfo, SingerInfo
from encrypt import encrypt

class NECCrawler(MusicCrawler):
    def __init__(self, csrf_token:str, cookie:str):
        super().__init__()
        self.csrf_token = csrf_token
        self.cookie = cookie
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

    def get_song_singer(self, song_id:str) -> str:
        return self.get_song_detail(song_id=song_id)["songs"][0]["artists"][0]["name"]

    def get_song_cover(self, song_id:str) -> base64:
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
    
    def get_singer_name(self, song_id:str) -> str:
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

    def get_singer_songs(self, singer_id:str) -> str:
        html_content = self._get_singer_data(singer_id=singer_id)
        pattern = r'<li><a href="/song\?id=\d+">(.*?)</a></li>'
        songs = re.findall(pattern, html_content)
        return songs

if __name__ == "__main__":
    cookie = r"_ntes_nnid=43d0a9152eefd1d52744655562e55797,1729407544382; _ntes_nuid=43d0a9152eefd1d52744655562e55797; WNMCID=dwsxzy.1729407545166.01.0; __snaker__id=waoxQcF2fxDIxtot; P_INFO=19112012800|1751007075|1|music|00&99|null&null&null#chq&null#10#0|&0|null|19112012800; MUSIC_U=00F77E6B2F87AC934FFD485275369FC8F5F7C8B23DB92408E00E2FD7C66931020C14D91A406F5FD2C3B592D0435C40EFF6D45E7C049FC4DCB25800EF70444062B3C8848F71CB6C3D7749AA83170023A5E961AD010FDD9BED6BC74278BB87A6798F31CFE291B6B6A93FBB392C838ED5CD463606C793829B0BE2AD6CD8B0280BCD615FE13B47D7A679E6FCC2A3CE0D531F85D0C22A9D533AC5AFFAB4B23F32B6F39A9E91493AC9A528E189D1CBF02887831611F8C05B65EF0B359068A427085B1B5B46C074D63E6CC4E5C6DC928959D58B456FA4D8D97267BFFC58D8A2D238AE8DE43E18494CADF15D2B220845927DFBC8847E0C223BE1988E5724A4FAAE0B03145B5239B4F31F7190989B761439A4042728607EED474D2F7166965884996C5B3A9BEB487D0E4FFD25EF2068B0BFC9991E34089A648A41BD49D6667D1F01D5E6F8AE3BDE4093E0A4D38517E39DA5CCDF30F9; __csrf=1db06a312a7d023e241d12a38384910c; __remember_me=true; gdxidpyhxdE=fnECaVxCS%5C2HzVbep3%2FIpWrSY3sinqaADYDzlbQWExjpN%5Cxs5iICiThvs9lmSaae4O%2FIQUb28MLrQI4VjoDYv061Z86u7Ldtr%2Bba68cqkJsLNEzxsaXUmmudfDSuCD97ECWeBwYjBJcmxb7K3gKz3NSSjntcAPEBubzq7tjA%2B3CKsrog%3A1751008628286; NMTID=00OSWVVYQnY-eNUGUjKhZEk__jepoMAAAGXsdnhHA; WEVNSM=1.0.0; WM_TID=h6qpg4uzMpNERURBEQaHTdnV2oMAlEfc; WM_NI=UAjEQ%2B7jSmZHPsmgii2DVYHo%2FrPZroxxaTFeczYSrDYHwL1KMb5%2BAlRSZP9I%2FoKs69FGAN5%2F8Qb5G0ET3TKPm%2B6ofepZOZWK7%2FtoHICUoWCYb%2B2xTlCZsVwMmYcN4qj9aDk%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8daa3fb49d8ad0cc5991ef8ba2c15f839a8badd76badebb7b3d86aafaca8d7b62af0fea7c3b92a979fa6a6d421f5b69d8ed94494ada388ec63f29c9abacb65edaea0bbf165bca8afb5c56fa1a697b4f1509b98b9adb4418fbefbccc468928d96b1bc43edb18594b53386998fafb825fc8faed6c63c878cfdb5ca5caff5fa90e56fb48681bbd641f5f1bc90cb43818ba1b8c253a2f5fe99d7688186bdb7f647af87adafb77baae7afa5ea37e2a3; _iuqxldmzr_=32; playerid=71245658; JSESSIONID-WYYY=vO85zh6xjFz3q%2B7JAY5AeVlC3GtTH2IYm42vTybf6cB9jAiqaVeyOMj7g%2Fwxtwir7zKu1hdxVGBMZr6CjoRxtO4oRKaCAYf3bD7ZJBm5NeyBZAxCRjfH3gTSIRoNZbzTaEPCatan0dvik2UU%2Bevci5pvqEHhad3dq1zw7RUTk7G5u8%5Ci%3A1751131284154"
    c = NECCrawler(csrf_token="1db06a312a7d023e241d12a38384910c", cookie=cookie)
    song_id = "333750"
    singer_id = "98110"

    # info = c.get_song_info(song_id=song_id)
    # info.save()

    info = c.get_singer_info(singer_id=singer_id)
    info.save()