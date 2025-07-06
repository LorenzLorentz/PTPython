import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import os
import re

# NLP
import gensim
from gensim.models.ldamulticore import LdaMulticore
from gensim.corpora import Dictionary
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer

# Visualization Libraries
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# Sentiment Analysis
from snownlp import SnowNLP
from statsmodels.nonparametric.smoothers_lowess import lowess

class Config:
    DATASET_PATH = "Data/all_songs.csv"
    OUTPUT_DIR = Path("result")

    NUM_TOPICS = 10
    LDA_PASSES = 10

    DECADE_BINS = [1980, 1990, 2000, 2010, 2020, 2030]
    DECADE_LABELS = ["1980s", "1990s", "2000s", "2010s", "2020s"]

    TOP_N_ARTISTS_FOR_ANALYSIS = 10
    ARTIST_CLUSTER_COUNT = 5

    @staticmethod
    def font_set():
        import matplotlib.font_manager as fm
        font_path = os.path.expanduser("~/.font/Arial Unicode.ttf")
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        font_name = font_prop.get_name()
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False 

class TopicAnalyzer:
    def __init__(self, tokenized_docs):
        print("Initializing LDA Topic Analyzer...")
        self.documents = [doc.split() for doc in tokenized_docs]
        self.dictionary = Dictionary(self.documents)
        self.dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.documents]
        self.model = None

    def train(self, num_topics:int, passes:int):
        print("Training LDA Topic Analyzer...")
        
        self.model = LdaMulticore(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=num_topics,
            passes=passes,
            workers=4,
        )

        return self.model

    def get_doc_topic(self, doc_tokens:str) -> list[float]:
        bow = self.dictionary.doc2bow(doc_tokens.split())
        dist = self.model.get_document_topics(bow, minimum_probability=0)
        return [prob for _, prob in dist]

    def save(self, path):
        with open(path, "w") as f:
            for idx, topic in self.model.print_topics(-1):
                f.write(f"Topic: {idx+1}\nWords: {topic}\n\n")

class ArtistAnalyzer:
    def __init__(self, df):
        self.df = df
        self.top_artists = self.df["singer_name"].value_counts().nlargest(Config.TOP_N_ARTISTS_FOR_ANALYSIS).index.tolist()

    def extract_characteristic_words(self, output_dir):
        """为Top N歌手提取特征词"""
        print("Extracting characteristic words for top artists...")
        all_lyrics = self.df["tokenized_lyric"].tolist()
        vectorizer = TfidfVectorizer()
        vectorizer.fit(all_lyrics) # 在全集上训练TF-IDF
        feature_names = np.array(vectorizer.get_feature_names_out())
        
        results = {}
        for artist in tqdm(self.top_artists, desc="Extracting Keywords"):
            artist_lyrics = self.df[self.df["singer_name"] == artist]["tokenized_lyric"].tolist()
            artist_tfidf_matrix = vectorizer.transform(artist_lyrics)
            # 计算每个词在该歌手所有歌曲中的平均TF-IDF值
            mean_tfidf = np.mean(artist_tfidf_matrix.toarray(), axis=0)
            # 排序并取最高分的词
            top_indices = mean_tfidf.argsort()[-20:][::-1]
            keywords = feature_names[top_indices]
            results[artist] = keywords.tolist()

        # 保存结果
        filepath = output_dir / "artist_characteristic_words.json"
        with open(filepath, "w", encoding="utf-8") as f:
            import json
            json.dump(results, f, ensure_ascii=False, indent=4)
        print(f"Artist characteristic words saved to {filepath}")

    def analyze_sentiment_arcs(self, output_dir):
        """分析并绘制Top N歌手的情感走向，包含平滑趋势线"""
        print("Analyzing sentiment arcs for top artists with trendlines...")
        plt.figure(figsize=(15, 12))
        
        # 使用颜色映射来为不同歌手分配不同颜色
        colors = plt.get_cmap('tab10').colors

        # 将所有散点汇集到一起，只绘制一次，作为背景
        overall_sentiments = []
        artist_sentiment_data = {} # 存储每个歌手的数据用于后续画趋势线

        # 第一遍循环：收集所有数据
        for artist in self.top_artists:
            artist_songs = self.df[self.df["singer_name"] == artist]["processed_lyric"]
            artist_sentiments = []
            
            for lyric in artist_songs:
                sentences = [s for s in lyric.split("\n") if s]
                if len(sentences) < 2: continue
                
                for i, sentence in enumerate(sentences):
                    try:
                        sentiment = SnowNLP(sentence).sentiments
                        # (句子在歌曲中的相对位置, 情感值)
                        position = i / (len(sentences) - 1)
                        artist_sentiments.append((position, sentiment))
                    except:
                        continue
            
            if artist_sentiments:
                overall_sentiments.extend(artist_sentiments)
                artist_sentiment_data[artist] = artist_sentiments

        # 绘制一次所有散点作为背景
        if overall_sentiments:
            all_x, all_y = zip(*overall_sentiments)
            plt.scatter(all_x, all_y, alpha=0.03, color='gray', label='All Sentence Sentiments (Background)')

        # 第二遍循环：为每个歌手计算并绘制平滑趋势线
        for i, artist in enumerate(self.top_artists):
            if artist in artist_sentiment_data:
                x, y = zip(*artist_sentiment_data[artist])
                
                if len(x) < 10: continue # 数据点太少则不绘制趋势线

                # ✨ 核心改进：使用 LOWESS 计算平滑曲线
                # frac 参数控制平滑度，值越大越平滑。0.2到0.8是常用范围。
                smoothed = lowess(y, x, frac=0.6, it=0)
                x_smooth, y_smooth = zip(*smoothed)
                
                # 绘制平滑后的趋势线
                plt.plot(x_smooth, y_smooth, linewidth=3.5, color=colors[i % len(colors)], label=f'{artist} (Trend)')

        plt.title("Sentiment Arc Analysis for Top Artists", fontsize=20)
        plt.xlabel("Normalized Position in Song (Start -> End)", fontsize=12)
        plt.ylabel("Sentiment (0: Negative -> 1: Positive)", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.ylim(-0.1, 1.1) # 设定Y轴范围
        filepath = output_dir / "sentiment_arc_analysis_with_trends.png"
        plt.savefig(filepath, dpi=150) # 提高图片分辨率
        plt.close()
        print(f"Sentiment arc analysis plot saved to {filepath}")

class Visualizer:
    @staticmethod
    def plot_topic_distribution_by_decade(song_df:pd.DataFrame):
        print("Analyzing topic distribution by decade...")
        
        decade_topic_dist = song_df.groupby("decade")[[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)]].mean()
        decade_topic_dist.plot(kind="bar", stacked=True, figsize=(15, 8), colormap="tab20")
        
        plt.title("Topic Distribution Across Decades", fontsize=16)
        plt.ylabel("Proportion of Topics")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(Config.OUTPUT_DIR, "decade_topic_distribution.png"))
        plt.close()

    def plot_word_frequency(self, df, output_dir):
        pass

    @staticmethod
    def plot_singer_cluster():
        pass

    @staticmethod
    def plot_wordclouds_all(df, output_dir):
        pass

    @staticmethod
    def plot_wordclouds_by_decade(df:pd.DataFrame, output_dir):
        print("Generating word clouds by decade...")
        for decade in tqdm(df["decade"].unique(), desc="Plotting Word Clouds"):
            decade_lyrics = " ".join(df[df["decade"] == decade]["tokenized_lyric"])
            
            wordcloud = WordCloud(
                font_path=os.path.expanduser("~/.font/Arial Unicode.ttf"),
                width=1000, height=600, background_color="white",
                colormap="viridis"
            ).generate(decade_lyrics)

            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation="bilinear")
            plt.axis("off")
            plt.title(f"Lyrics Word Cloud - {decade}", fontsize=20)
            plt.savefig(os.path.join(output_dir, "wordcloud", f"wordcloud_{decade}.png"))
            plt.close()

    @staticmethod
    def plot_wordclouds_by_cluster(df, artist_clusters_df, output_dir):
        print("Generating word clouds by cluster...")
        for cluster_id in sorted(artist_clusters_df['cluster'].unique()):
            artists_in_cluster = artist_clusters_df[artist_clusters_df['cluster'] == cluster_id].index.tolist()
            cluster_lyrics_series = df[df['singer_name'].isin(artists_in_cluster)]['tokenized_lyric']
            text_for_wordcloud = " ".join(cluster_lyrics_series.dropna())
            if not text_for_wordcloud.strip():
                print(f"Skipping Cluster {cluster_id} as it has no associated lyrics.")
                continue
            
            wordcloud = WordCloud(
                font_path=os.path.expanduser("~/.font/Arial Unicode.ttf"),
                width=1000, height=600, background_color='white',
                colormap='plasma'
            ).generate(text_for_wordcloud)
            
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'Word Cloud for Artist Cluster {cluster_id}\n({len(artists_in_cluster)} artists)', fontsize=20)

            display_artists = ", ".join(artists_in_cluster[:5])
            if len(artists_in_cluster) > 5:
                display_artists += ", ..."
            plt.figtext(0.5, 0.05, display_artists, ha="center", fontsize=10, style='italic')

            filepath = output_dir / f'wordcloud_cluster_{cluster_id}.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()

def analyze_decade(df:pd.DataFrame):
    Visualizer.plot_topic_distribution_by_decade(df=df)
    Visualizer.plot_wordclouds_by_decade(Config.OUTPUT_DIR)
    
def analyze_singer(df:pd.DataFrame):
    print("Clustering artists based on topic distribution...")
    artist_topic_dist = df.groupby("singer_name")[[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)]].mean()
    valid_artists = artist_topic_dist[df["singer_name"].value_counts() > 5] 
    
    kmeans = KMeans(n_clusters=Config.ARTIST_CLUSTER_COUNT, random_state=42, n_init=10)
    valid_artists["cluster"] = kmeans.fit_predict(valid_artists)
    valid_artists[["cluster"]].to_csv(Config.OUTPUT_DIR / "artist_clusters.csv")
    print("Artist clustering results saved.")

    # --- 执行任务二：词云图 ---
    Visualizer.plot_wordclouds_by_decade(Config.OUTPUT_DIR)

    # --- 执行任务三：歌手分析 ---
    artist_analyzer = ArtistAnalyzer(df)
    artist_analyzer.extract_characteristic_words(Config.OUTPUT_DIR)
    artist_analyzer.analyze_sentiment_arcs(Config.OUTPUT_DIR)
    
    print("\n✅ All tasks completed successfully!")
    print(f'Find all results in the "{Config.OUTPUT_DIR}" directory.')

def main():
    Config.OUTPUT_DIR.mkdir(exist_ok=True)
    Config.font_set()
   
    print("Loading Data and Processing Data ...")
    df = pd.read_csv(Config.DATASET_PATH)
    df["decade"] = pd.cut(df["release_year"], bins=Config.DECADE_BINS, labels=Config.DECADE_LABELS, right=False)
    df.dropna(subset=["tokenized_lyric", "decade"], inplace=True)

    topic_modeler = TopicModeler(df["tokenized_lyric"])
    lda_model = topic_modeler.train(Config.NUM_TOPICS, Config.LDA_PASSES)
    topic_modeler.save(os.path.join(Config.OUTPUT_DIR, "lda_result.txt"))

    topic_dists = df["tokenized_lyric"].apply(lambda x: topic_modeler.get_doc_topic(x))
    topic_df = pd.DataFrame(topic_dists.tolist(), index=df.index, columns=[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)])
    df = pd.concat([df, topic_df], axis=1)

if __name__ == "__main__":
    main()