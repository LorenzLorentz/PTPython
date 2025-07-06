import pandas as pd
import json
import re
import jieba
from pathlib import Path
from tqdm import tqdm

SINGER_DIR = Path("../crawler/Data/Singer")
SONG_DIR = Path("../crawler/Data/Song")
OUTPUT_CSV = "Data/all_songs.csv"

STOPWORDS = set()
with open("Data/hit_stopwords.txt", "r", encoding="utf-8") as f:
    for line in f:
        stripped_line = line.strip()
        if stripped_line:
            words = stripped_line.split()
            STOPWORDS.update(words)

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
            song_lyric = song_info.get("song_lyric")
            
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
    songs_df = load_songs(SONG_DIR)
    songs_df['release_year'] = songs_df['song_time'].str.extract(r'(\d{4})').astype(int)
    songs_df.info()
    songs_df.head()
    songs_df.to_csv(OUTPUT_CSV)

if __name__ == "__main__":
    main()