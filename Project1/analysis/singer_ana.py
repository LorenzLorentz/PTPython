import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import json

from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from snownlp import SnowNLP

from config import Config

class SingerAnalyzer:
    def __init__(self, df: pd.DataFrame):
        """预处理, 获得top singers"""

        self.df = df
        self.singer_song_cnt = self.df["singer_name"].value_counts()
        self.top_singers = self.singer_song_cnt.nlargest(20).index.tolist()

    def cluster_singers(self, n_clusters:int) -> pd.DataFrame:
        """根据歌曲主题分布聚类歌手"""
        
        print("Clustering singers based on topic distribution...")
        
        # 计算歌手的歌曲主题分布
        singer_topic_dist = self.df.groupby("singer_name")[[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)]].mean()

        # 通过kmeans算法聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        singer_topic_dist["cluster"] = kmeans.fit_predict(singer_topic_dist)
        
        return singer_topic_dist

    def extract_charac_words(self, output_path: Path):
        """通过tf-idf提取(部分)歌手特征词汇"""

        print("Extracting characteristic words for top artists...")
        
        # 获取所有歌词, 并进行tf-idf向量化
        all_lyrics = self.df["tokenized_lyric"].tolist()
        vectorizer = TfidfVectorizer(max_features=2000)
        vectorizer.fit(all_lyrics)
        dic = np.array(vectorizer.get_feature_names_out())
        
        results = {}
        for artist in tqdm(self.top_singers, desc="Extracting Keywords"):
            # 获取歌手的所有歌词
            singer_lyrics = self.df[self.df["singer_name"] == artist]["tokenized_lyric"].tolist()
            tfidf_matrix = vectorizer.transform(singer_lyrics)
            
            # 计算平均tf-idf向量
            mean_tfidf = np.mean(tfidf_matrix.toarray(), axis=0)
            top_indices = mean_tfidf.argsort()[-20:][::-1]
            
            # 获得关键词
            keywords = dic[top_indices]
            results[artist] = keywords.tolist()

        with open(output_path, "w") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)

    def get_sentiment(self) -> dict:
        """计算(部分)歌手歌曲情感数据"""

        print("Calculating sentiment arcs data for top artists...")
        
        singer_sentiment_data = {}
        for singer in tqdm(self.top_singers, desc="Calculating Sentiment"):
            songs = self.df[self.df["singer_name"] == singer]["processed_lyric"]
            sentiments = []
            
            for lyric in songs:
                # 将歌词划分为乐句
                sentences = [s for s in str(lyric).split("\n") if s.strip()]
                
                # 对每个乐句, 计算其位置与情感分数
                for i, sentence in enumerate(sentences):
                    try:
                        sentiment = SnowNLP(sentence).sentiments
                        position = i/(len(sentences)-1) if len(sentences) > 1 else 0.5
                        sentiments.append((position, sentiment))
                    except Exception:
                        continue

            singer_sentiment_data[singer] = sentiments
        
        return singer_sentiment_data

    def get_sentiment_by_cluster(self, df:pd.DataFrame, singer_clusters_df:pd.DataFrame) -> dict:
        """计算所有歌手歌曲情感数据"""

        print("Calculating sentiment arcs data by singer cluster...")
        
        cluster_sentiment_data = {}

        for cluster_id in tqdm(singer_clusters_df['cluster'].unique(), desc="Calculating Sentiment by Cluster"):
            # 获得聚类所有歌曲数据
            artists_in_cluster = singer_clusters_df[singer_clusters_df['cluster'] == cluster_id].index.tolist()
            cluster_lyrics = df[df['singer_name'].isin(artists_in_cluster)]['processed_lyric']
            
            cluster_sentiments = []
            
            for lyric in cluster_lyrics:
                # 将歌词划分为乐句
                sentences = [s for s in str(lyric).split("\n") if s.strip()]
                
                # 对每个乐句, 计算其位置与情感分数
                for i, sentence in enumerate(sentences):
                    try:
                        sentiment = SnowNLP(sentence).sentiments
                        position = i/(len(sentences)-1)
                        cluster_sentiments.append((position, sentiment))
                    except Exception:
                        continue
            
            if cluster_sentiments:
                cluster_sentiment_data[cluster_id] = cluster_sentiments
        
        return cluster_sentiment_data

    def analyze_vocabulary_richness(self) -> dict:
        """分析歌手的歌词文本词汇丰富度"""
        
        print("Analyzing singer vocabulary richness...")

        artist_stats = []
        for artist, group in tqdm(self.df.groupby("singer_name"), desc="Calculating Vocabulary Metrics"):
            # 计算总词数和罕见词数
            tot_words = group["tot_word_cnt"].sum()
            tot_rare_words = group["rare_word_cnt"].sum()

            # 计算总独特词数
            all_tokens = [word for lyric in group["tokenized_lyric"] for word in lyric.split()]
            tot_unique_words = len(set(all_tokens))
            
            # 计算丰富度和罕见度
            diverse_word_ratio = tot_unique_words / tot_words
            rare_word_rate = tot_rare_words / tot_words
            
            artist_stats.append({
                'singer_name': artist,
                'song_count': len(group),
                'diverse_word_ratio': diverse_word_ratio,
                'rare_word_ratio': rare_word_rate
            })

        # 构建df, 并按指标排序获取结果
        result_df = pd.DataFrame(artist_stats).set_index("singer_name")
        top_diverse = result_df.sort_values(by='diverse_word_ratio', ascending=False)
        top_rare = result_df.sort_values(by='rare_word_ratio', ascending=False)

        return {
            "diverse": top_diverse,
            "rare": top_rare
        }