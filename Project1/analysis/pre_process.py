import pandas as pd
import json
import re
import jieba
from pathlib import Path
from tqdm import tqdm

# 相关文件夹信息
SINGER_DIR = Path("../crawler/Data/Singer")
SONG_DIR = Path("../crawler/Data/Song")
OUTPUT_CSV = "Data/all_songs.csv"

# 获取停用词
STOPWORDS = set()
with open("Data/hit_stopwords.txt", "r", encoding="utf-8") as f:
    for line in f:
        stripped_line = line.strip()
        if stripped_line:
            words = stripped_line.split()
            STOPWORDS.update(words)

def process_lyric(lyric:str) -> dict:
    """处理歌词"""

    # 去除时间戳、时长等信息
    lyric = re.sub(r'\[\d{2}:\d{2}\.\d{2,3}\]', "", lyric)
    lyric = re.sub(r'\[.*?\]', "", lyric)

    # 去除制作人、编曲等信息
    lines = lyric.split('\n')
    kept_lines = []
    for line in lines:
        if not line.strip():
            continue
        if re.search(r"\s+:\s+", line) or re.search("：", line):
            continue
        kept_lines.append(line)
    
    # 重建处理后歌词
    lyric = "\n".join(kept_lines)
    lyric = lyric.strip()

    # 利用jieba库分词, 并去除停用词
    words = [word for word in jieba.lcut(lyric) if word.strip() and word not in STOPWORDS and len(word) > 1]
    
    # 构建分词后歌词, 记录其他数值信息
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
    """处理所有歌曲"""

    all_songs = []
    
    # 加载所有歌曲json文件
    song_files = list(song_dir.glob('*.json'))
    for song_file in tqdm(song_files, desc="Processing songs"):
        with open(song_file, "r", encoding="utf-8") as f:
            # 加载歌曲
            song_info = json.load(f)
            song_lyric = song_info.get("song_lyric")
            
            # 保存所需信息
            song = {
                "song_id": song_info.get("song_id"),
                "song_name": song_info.get("song_name"),
                "singer_id": song_info.get("song_singer")[0],
                "singer_name": song_info.get("song_singer")[1],
                "song_time": song_info.get("song_time"),
                **process_lyric(song_lyric)
            }

            all_songs.append(song)

    return pd.DataFrame.from_records(all_songs)

def main():
    # 处理所有歌曲
    songs_df = load_songs(SONG_DIR)

    # 加入发行年份信息
    songs_df['release_year'] = songs_df['song_time'].str.extract(r'(\d{4})').astype(int)
    
    # 展示相关信息并保存
    songs_df.info()
    songs_df.head()
    songs_df.to_csv(OUTPUT_CSV)

if __name__ == "__main__":
    main()