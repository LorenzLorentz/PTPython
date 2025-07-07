import pandas as pd
from collections import Counter
import re

class LyricAnalyzer:
    def __init__(self, df:pd.DataFrame):
        self.df = df

    def calc_word_freq(self, top_n:int=20) -> list:
        """词频统计"""

        print("Calculating word frequencies...")

        # 获得所有中文词汇
        all_words = []
        for lyric in self.df['tokenized_lyric'].dropna():
            for word in lyric.split():
                if re.fullmatch(r'[\u4e00-\u9fa5]+', word): # 只保留中文字符
                    all_words.append(word)
        
        # 获得词频top_n的词汇
        freq = Counter(all_words).most_common(top_n)
        
        return freq

    def stat_rare_words(self) -> pd.DataFrame:
        """生僻词统计"""

        print("Stating rare words...")
        
        # 统计词频, 定义生僻词
        all_words = [word for lyric in self.df["tokenized_lyric"].dropna() for word in lyric.split()]
        word_counts = Counter(all_words)
        rare_words_set = {word for word, count in word_counts.items() if count <= 5}
        
        # 计算生僻词数量
        def cnt_rare_words(tokenized_lyric):
            if not isinstance(tokenized_lyric, str): return 0
            return len([word for word in tokenized_lyric.split() if word in rare_words_set])
        self.df["rare_word_cnt"] = self.df["tokenized_lyric"].apply(cnt_rare_words)
        
        return self.df