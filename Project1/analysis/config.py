from pathlib import Path
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

class Config:
    # 路径参数
    DATASET_PATH = "Data/all_songs.csv"
    OUTPUT_DIR = Path("result")
    WORDCLOUD_DIR = OUTPUT_DIR / "wordclouds"

    # LDA模型参数
    NUM_TOPICS = 10
    LDA_PASSES = 10

    # 年代划分参数
    DECADE_BINS = [1980, 1990, 2000, 2010, 2020, 2030]
    DECADE_LABELS = ["1980s", "1990s", "2000s", "2010s", "2020s"]

    # 歌手分析参数
    MIN_SONG_COUNT_FOR_ARTIST = 5
    ARTIST_CLUSTER_COUNT = 5

    @staticmethod
    def setup_environment():
        Config.OUTPUT_DIR.mkdir(exist_ok=True)
        Config.WORDCLOUD_DIR.mkdir(exist_ok=True)

        # 配置字体
        font_path = os.path.expanduser("~/.font/Arial Unicode.ttf") 
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        font_name = font_prop.get_name()
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False