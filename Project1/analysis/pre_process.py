import pandas as pd
import json
import re
import jieba
from pathlib import Path
from tqdm import tqdm
from functools import lru_cache
from crawler.NECCrawler import NECCrawler
from datetime import datetime

SINGER_DIR = Path("crawler/Data/Singer")
SONG_DIR = Path("crawler/Data/Song")
OUTPUT_CSV = "analysis/Data/all_songs.csv"
STOPWORDS = {
    # --- 标点符号 ---
    ' ', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.',
    '/', ':', ';', '<', '=', '>', '?', '@', '[', '\\', ']', '^', '_', '`', 
    '{', '|', '}', '~', '！', '“', '”', '＃', '￥', '％', '＆', '（', '）',
    '＊', '＋', '，', '－', '．', '／', '：', '；', '＜', '＝', '＞', '？',
    '＠', '【', '】', '＾', '＿', '｀', '｛', '｜', '｝', '～', '、', '。',
    '《', '》', '「', '」', '『', '』', '【', '】', '〔', '〕', '〖', '〗',
    '〘', '〙', '〚', '〛', '…', '...', '⋯', '..', '.......',
    '\n', '\t', '\r', '\u3000',
    # 助词
    '的', '地', '得', '之',
    # 拟声词
    'lah', 'loh', 'meh', 'ooh', 'uh', 'uhm', 'umm',
    'la', 'oh', 'ah',
}

@lru_cache(maxsize=None)
def _get_crawler() -> NECCrawler:
    return NECCrawler(cookie=r"_ntes_nnid=43d0a9152eefd1d52744655562e55797,1729407544382; _ntes_nuid=43d0a9152eefd1d52744655562e55797; WNMCID=dwsxzy.1729407545166.01.0; __snaker__id=waoxQcF2fxDIxtot; P_INFO=19112012800|1751007075|1|music|00&99|null&null&null#chq&null#10#0|&0|null|19112012800; __remember_me=true; NMTID=00OSWVVYQnY-eNUGUjKhZEk__jepoMAAAGXsdnhHA; WEVNSM=1.0.0; WM_TID=h6qpg4uzMpNERURBEQaHTdnV2oMAlEfc; _iuqxldmzr_=32; JSESSIONID-WYYY=%2B5IbJY2dKDi9x22B5YMT5AfK2mVBWzyiHOABV84jkbcpsz%5C1Dudd1po1%2FJyaQOyj7STg4UgdM77fDww9Yhv3PVlIQke%5C9YFPbBumCaBluBaupYb3Bi1N1JRjVmxAGfBJS40clzO%2BGUU2kOYpWXvkCFW224PJrHT%5CIZ%5C7YRh7JhR%2B7XRC%3A1751686660883; WM_NI=gYgXZDjLX%2FTtA7lhT%2B1NBYfg5JIfo%2BPeNjrBkwr0y%2B3vqPxvj%2FhxVsB42FvZn2AaUdXfUAtuwHFUsctgFFMSaWdDzWTG5S3Ioqh3pZyxUJlq1X66ZnhKaPCmUeY1zpnpZXU%3D; WM_NIKE=9ca17ae2e6ffcda170e2e6ee8aae54878cbb8ddb3f959e8ba3c54e828b8f87db48f5bb9e8cfb6f97bd9cb4b52af0fea7c3b92aa587a9b9d950aa9498d0d78083e9a489d721f3928ebae56df7968787ee2194bb828bf14aa9a9bed1fc21f1aabfb1fb7eaaf1a899d57982ecfea7f552aeee8f82d8709cba9ba2f77fb5988ab6f269b8b98aa7d059a389aca5f95d9899fbb4b243adafa8d4f352bba89babef7bf388fad7d966ac95afb1c26797bb97d2f97caeb096b9d837e2a3; gdxidpyhxdE=GeMD%2FxzVeIL6CkZvu4eGX%5CHxU19a4DGwVRz5187I4N%2FM%5CTCbPeknH5DiOmrNAP5L2zIGp61%2B83Isam4v0Jjgzu8OHK0%5C0vkgBy3z9frnZm%2FczG8%2BGjO5r6dnIiKAz8vg%5CJIYJyUyAETr0JCs17Ja4p%2FBlMngNjIc759zM%2BgwQ57iKYGi%3A1751686006333; MUSIC_U=00B3C60E6609EAE4EBC34EB5795A71825370B3FA9DF9F7CEDB148312A53AFEBAB4E9937E04B4765A288D0D6E901AB9D4F50E31662CB04DC6007874167639B3B73582A1C223D68189644D124953A365D53D51B272393BEFEEE907446077DA99EC2D0A82808FD65D502B23CC1D09DE5F253244C1A80ED76D18CD9A7A59259C60BA58F34E944FB8F67AEF2959CEBE4A2F4403CDA4A4BF92540F8A612B2681881AA2BAC77DAD7FA584906585CDD12C6F7BA373938F399D9EA3E2E0A922667374045551E1F8D2CD9308D76388B071DDA34272272EAB10033FEE8B0CD0C78ED6DA74D5BCB2B30790490231D29CC9008B32E99ECC25FFB506AB5AAEE6CE0BC4C3EFA2B6B947BF7DFEED91F5CC681AFF6A008EE3BE7FA15B7C015BB5530170024C80984DDA891068247397D97DD305CD6D45541E6B40DB184E4576EB4A340555743C5838669FAFED11F5A82C3F088BA20ED651AE3D; __csrf=53c86040ce0cea0d00f4e1220bd29fd5")

def get_time(song_id:str):
    time = _get_crawler().get_song_time(song_id=song_id)
    return datetime.fromtimestamp(time/1000).strftime('%Y-%m-%d')

def process_lyric(lyric:str) -> dict:    
    lyric = re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]', "", lyric)
    lyric = re.sub(r'\[.*?\]', "", lyric)

    lines = lyric.split('\n')
    kept_lines = []
    for line in lines:
        if not line.strip():
            continue
        if re.search(r"\s+:\s+", line) or re.search("：", line):
            continue
        kept_lines.append(line)
    
    lyric = "\n".join(kept_lines)
    lyric = lyric.strip()

    words = [word for word in jieba.lcut(lyric) if word.strip() and word not in STOPWORDS and len(word) > 1]
    
    tokenized_lyric = " ".join(words)
    unique_word_cnt = len(set(words))
    tot_word_cnt = len(words)

    return {
        "processed_lyric": lyric,
        "tokenized_lyric": tokenized_lyric,
        "len": len(lyric),
        "unique_word_cnt": unique_word_cnt,
        "tot_word_cnt": tot_word_cnt
    }

def load_songs(song_dir:Path) -> pd.DataFrame:
    all_songs = []
    song_files = list(song_dir.glob('*.json'))
    for song_file in tqdm(song_files, desc="Processing songs"):
        with open(song_file, "r", encoding="utf-8") as f:
            song_info = json.load(f)
            song_id = song_info.get("song_id")
            song_lyric = song_info.get("song_lyric")
            # song_time = get_time(song_id=song_id)
            
            song = {
                "song_id": song_id,
                "song_name": song_info.get("song_name"),
                "singer_id": song_info.get("song_singer")[0],
                "singer_name": song_info.get("song_singer")[1],
                **process_lyric(song_lyric)
            }

            all_songs.append(song)

    return pd.DataFrame.from_records(all_songs)

def main():
    songs_df = load_songs(SONG_DIR)
    songs_df.info()
    songs_df.head()
    songs_df.to_csv(OUTPUT_CSV)