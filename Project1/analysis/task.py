import pandas as pd
import numpy as np
from pathlib import Path
from tqdm import tqdm
import os
import json
from collections import Counter
import re

# NLP & ML
import gensim
from gensim.models.ldamulticore import LdaMulticore
from gensim.corpora import Dictionary
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import PCA

# Visualization Libraries
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud

# Sentiment Analysis
from snownlp import SnowNLP
from statsmodels.nonparametric.smoothers_lowess import lowess

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

        font_path = os.path.expanduser("~/.font/Arial Unicode.ttf") 
        fm.fontManager.addfont(font_path)
        font_prop = fm.FontProperties(fname=font_path)
        font_name = font_prop.get_name()
        plt.rcParams['font.family'] = font_name
        plt.rcParams['axes.unicode_minus'] = False 

class TopicAnalyzer:
    def __init__(self, tokenized_docs: list[str]):
        print("Initializing Topic Analyzer...")
        self.documents = [doc.split() for doc in tokenized_docs]
        self.dictionary = Dictionary(self.documents)
        self.dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.documents]
        self.model = None

    def train(self, num_topics: int, passes: int) -> LdaMulticore:
        print(f"Training LDA model with {num_topics} topics...")
        self.model = LdaMulticore(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=num_topics,
            passes=passes,
            workers=os.cpu_count() - 1 or 1,
        )
        return self.model

    def get_doc_topic_dist(self, doc_tokens: str) -> list[float]:
        bow = self.dictionary.doc2bow(doc_tokens.split())
        dist = self.model.get_document_topics(bow, minimum_probability=0)
        return [prob for _, prob in dist]

    def save_topics(self, path: Path):
        print(f"Saving topics to {path}...")
        with open(path, "w", encoding="utf-8") as f:
            for idx, topic in self.model.print_topics(-1, num_words=15):
                f.write(f"Topic: {idx+1}\nWords: {topic}\n\n")

class ArtistAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.artist_song_counts = self.df["singer_name"].value_counts()
        self.top_artists = self.artist_song_counts.nlargest(20).index.tolist()

    def cluster_artists(self, n_clusters: int) -> pd.DataFrame:
        print("Clustering artists based on topic distribution...")
        artist_topic_dist = self.df.groupby("singer_name")[[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)]].mean()
        valid_artists_idx = self.artist_song_counts[self.artist_song_counts >= Config.MIN_SONG_COUNT_FOR_ARTIST].index
        valid_artists_dist = artist_topic_dist.loc[valid_artists_idx]
        
        if len(valid_artists_dist) < n_clusters:
            print(f"Warning: Valid artists ({len(valid_artists_dist)}) less than n_clusters ({n_clusters}). Clustering skipped.")
            return None

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        valid_artists_dist["cluster"] = kmeans.fit_predict(valid_artists_dist)
        return valid_artists_dist

    def extract_characteristic_words(self, output_path: Path):
        print("Extracting characteristic words for top artists...")
        all_lyrics = self.df["tokenized_lyric"].tolist()
        vectorizer = TfidfVectorizer(max_features=2000)
        vectorizer.fit(all_lyrics)
        feature_names = np.array(vectorizer.get_feature_names_out())
        
        results = {}
        for artist in tqdm(self.top_artists, desc="Extracting Artist Keywords"):
            artist_lyrics = self.df[self.df["singer_name"] == artist]["tokenized_lyric"].tolist()
            if not artist_lyrics: continue
            
            artist_tfidf_matrix = vectorizer.transform(artist_lyrics)
            mean_tfidf = np.mean(artist_tfidf_matrix.toarray(), axis=0)
            top_indices = mean_tfidf.argsort()[-20:][::-1]
            keywords = feature_names[top_indices]
            results[artist] = keywords.tolist()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=4)
    
    def get_sentiment_data(self) -> dict:
        print("Calculating sentiment arcs data for top artists...")
        artist_sentiment_data = {}
        for artist in tqdm(self.top_artists, desc="Analyzing Artist Sentiments"):
            artist_songs = self.df[self.df["singer_name"] == artist]["processed_lyric"]
            artist_sentiments = []
            
            for lyric in artist_songs:
                sentences = [s for s in str(lyric).split("\n") if s.strip()]
                if len(sentences) < 2: continue
                
                for i, sentence in enumerate(sentences):
                    try:
                        sentiment = SnowNLP(sentence).sentiments
                        position = i / (len(sentences) - 1) if len(sentences) > 1 else 0.5
                        artist_sentiments.append((position, sentiment))
                    except Exception:
                        continue
            
            if artist_sentiments:
                artist_sentiment_data[artist] = artist_sentiments
        
        return artist_sentiment_data

    def get_sentiment_data_for_plotting(self) -> dict:
        print("Calculating sentiment arcs data for top artists...")
        artist_sentiment_data = {}
        for artist in tqdm(self.top_artists, desc="Analyzing Artist Sentiments"):
            artist_songs = self.df[self.df["singer_name"] == artist]["processed_lyric"]
            artist_sentiments = []
            
            for lyric in artist_songs:
                sentences = [s for s in str(lyric).split("\n") if s.strip()]
                if len(sentences) < 2: continue
                
                for i, sentence in enumerate(sentences):
                    try:
                        sentiment = SnowNLP(sentence).sentiments
                        position = i / (len(sentences) - 1) if len(sentences) > 1 else 0.5
                        artist_sentiments.append((position, sentiment))
                    except Exception:
                        continue
            
            if artist_sentiments:
                artist_sentiment_data[artist] = artist_sentiments
        
        return artist_sentiment_data

    def analyze_sentiment_by_cluster(self, df: pd.DataFrame, artist_clusters_df: pd.DataFrame) -> dict:
        print("Analyzing sentiment data by artist cluster...")
        if artist_clusters_df is None or 'cluster' not in artist_clusters_df.columns:
            return {}

        cluster_sentiment_data = {}

        for cluster_id in tqdm(artist_clusters_df['cluster'].unique(), desc="Calculating Sentiment by Cluster"):
            artists_in_cluster = artist_clusters_df[artist_clusters_df['cluster'] == cluster_id].index.tolist()
            cluster_lyrics = df[df['singer_name'].isin(artists_in_cluster)]['processed_lyric']
            
            cluster_sentiments = []
            
            for lyric in cluster_lyrics:
                sentences = [s for s in str(lyric).split("\n") if s.strip()]
                if len(sentences) < 2: continue
                
                for sent_idx, sentence in enumerate(sentences):
                    try:
                        sentiment = SnowNLP(sentence).sentiments
                        position = sent_idx / (len(sentences) - 1)
                        cluster_sentiments.append((position, sentiment))
                    except Exception:
                        continue
            
            if cluster_sentiments:
                cluster_sentiment_data[cluster_id] = cluster_sentiments
                
        return cluster_sentiment_data

    def analyze_vocabulary_richness(self) -> dict:
        """
        分析歌手的词汇丰富度。
        1. 词汇多样性 (独特词 / 总词数)
        2. 生僻词使用率 (生僻词数 / 总词数)
        返回一个包含两个排名后DataFrame的字典。
        """
        print("Analyzing artist vocabulary richness...")

        # 筛选出歌曲数量过少的歌手，避免统计偏差
        valid_artists = self.artist_song_counts[self.artist_song_counts >= Config.MIN_SONG_COUNT_FOR_ARTIST].index
        df_filtered = self.df[self.df['singer_name'].isin(valid_artists)].copy()
        
        artist_stats = []
        # 按歌手分组进行精细计算
        for artist, group in tqdm(df_filtered.groupby('singer_name'), desc="Calculating Vocabulary Metrics"):
            # 聚合基础数据
            total_words = group['tot_word_cnt'].sum()
            total_rare_words = group['rare_word_cnt'].sum()
            
            if total_words == 0:
                continue

            # 计算该歌手所有歌曲的“总独特词数”，需要合并所有歌词再计算
            all_tokens = [word for lyric in group['tokenized_lyric'] for word in lyric.split()]
            total_unique_words = len(set(all_tokens))
            
            # 计算比率
            lexical_diversity_ratio = total_unique_words / total_words
            rare_word_rate = total_rare_words / total_words
            
            artist_stats.append({
                'singer_name': artist,
                'song_count': len(group),
                'lexical_diversity_ratio': lexical_diversity_ratio,
                'rare_word_rate': rare_word_rate
            })

        if not artist_stats:
            print("No sufficient artist data to analyze vocabulary richness.")
            return None

        # 创建结果DataFrame
        result_df = pd.DataFrame(artist_stats).set_index('singer_name')

        # 分别按两个指标排序
        top_diversity = result_df.sort_values(by='lexical_diversity_ratio', ascending=False)
        top_rare_word_users = result_df.sort_values(by='rare_word_rate', ascending=False)

        return {
            "diversity": top_diversity,
            "rare_words": top_rare_word_users
        }

class LyricAnalyzer:
    def __init__(self, df: pd.DataFrame):
        self.df = df

    def calculate_word_frequencies(self, top_n:int=20) -> dict:
        print("Calculating word frequencies...")

        all_words_with_stopwords = []
        for lyric in self.df['processed_lyric'].dropna():
            all_words_with_stopwords.extend(re.findall(r'[\u4e00-\u9fa5]+', lyric))
        freq_with_stopwords = Counter(all_words_with_stopwords).most_common(top_n)
        
        all_words_without_stopwords = []
        for lyric in self.df['tokenized_lyric'].dropna():
            for word in lyric.split():
                if re.fullmatch(r'[\u4e00-\u9fa5]+', word):
                    all_words_without_stopwords.append(word)
        freq_without_stopwords = Counter(all_words_without_stopwords).most_common(top_n)
        
        return {
            "with_stopwords": freq_with_stopwords,
            "without_stopwords": freq_without_stopwords
        }

    def analyze_lyric_metrics(self) -> pd.DataFrame:
        print("Analyzing lyric metrics (length, unique words, rare words)...")
        
        # 1. 统计整个语料库的词频以定义“生僻词”
        print("  - Identifying rare words across all lyrics...")
        all_words = [word for lyric in self.df['tokenized_lyric'].dropna() for word in lyric.split()]
        word_counts = Counter(all_words)
        # 定义生僻词为在所有歌曲中只出现过1次的词
        rare_words_set = {word for word, count in word_counts.items() if count <= 5}
        print(f"  - Found {len(rare_words_set)} rare words (words appearing only once in the corpus).")

        # 2. 计算每首歌的生僻词数量
        def count_rare_words(tokenized_lyric):
            if not isinstance(tokenized_lyric, str): return 0
            return len([word for word in tokenized_lyric.split() if word in rare_words_set])

        self.df['rare_word_cnt'] = self.df['tokenized_lyric'].apply(count_rare_words)
        
        # 打印统计摘要
        print("Summary of Lyric Metrics:")
        metrics_summary = self.df[['len', 'unique_word_cnt', 'tot_word_cnt', 'rare_word_cnt']].describe()
        print(metrics_summary)
        
        return self.df

class Visualizer:
    @staticmethod
    def plot_wordclouds_by_decade(df:pd.DataFrame, output_dir:Path):
        print("Generating word clouds by decade...")
        for decade in tqdm(df["decade"].unique(), desc="Plotting Decade Word Clouds"):
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
            plt.savefig(output_dir / f"wordcloud_{decade}.png", dpi=250, bbox_inches='tight')
            plt.close()

    @staticmethod
    def plot_topic_by_decade(song_df:pd.DataFrame, output_dir:Path):
        print("Plotting topic distribution across decades...")
        decade_topic_dist = song_df.groupby("decade")[[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)]].mean()
        
        plt.figure(figsize=(15, 8))
        decade_topic_dist.plot(kind="bar", stacked=True, figsize=(15, 8), colormap="tab20", ax=plt.gca())
        
        plt.title("Topic Distribution Across Decades", fontsize=16)
        plt.ylabel("Proportion of Topics", fontsize=12)
        plt.xlabel("Decade", fontsize=12)
        plt.xticks(rotation=45)
        plt.legend(title="Topics", bbox_to_anchor=(1.02, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(output_dir / "decade_topic_dist.png", dpi=250)
        plt.close()

    @staticmethod
    def plot_artist_clusters(artist_clusters_df:pd.DataFrame, output_path:Path):
        print("Plotting artist clusters...")

        topic_cols = [col for col in artist_clusters_df.columns if col.startswith('Topic_')]
        
        X = artist_clusters_df[topic_cols].values
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X)
        
        plt.figure(figsize=(16, 12))
        clusters = artist_clusters_df['cluster']
        unique_clusters = sorted(clusters.unique())

        scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='tab10', s=100, alpha=0.7)

        for i, artist_name in enumerate(artist_clusters_df.index):
            plt.text(X_pca[i, 0], X_pca[i, 1] + 0.005, artist_name, ha='center', va='bottom', fontsize=9, alpha=0.8)

        plt.title('Artist Clusters based on Lyric Topics (PCA)', fontsize=20)
        plt.xlabel('Principal Component 1', fontsize=12)
        plt.ylabel('Principal Component 2', fontsize=12)
        plt.legend(handles=scatter.legend_elements()[0], labels=[f"Cluster {c}" for c in unique_clusters], title="Clusters")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Artist cluster plot saved to {output_path}")

    @staticmethod
    def plot_wordclouds_by_cluster(df:pd.DataFrame, artist_clusters_df:pd.DataFrame, output_dir:Path):
        print("Generating word clouds by artist cluster...")
        if artist_clusters_df is None or 'cluster' not in artist_clusters_df.columns:
            print("Skipping cluster word cloud generation due to insufficient data.")
            return
        
        for cluster_id in tqdm(sorted(artist_clusters_df['cluster'].unique()), desc="Plotting Cluster Word Clouds"):
            artists_in_cluster = artist_clusters_df[artist_clusters_df['cluster'] == cluster_id].index.tolist()
            text_for_wordcloud = " ".join(df[df['singer_name'].isin(artists_in_cluster)]['tokenized_lyric'].dropna())
            if not text_for_wordcloud.strip(): continue
            
            wordcloud = WordCloud(
                font_path=os.path.expanduser("~/.font/Arial Unicode.ttf"),
                width=1000, height=600, background_color='white',
                colormap='plasma'
            ).generate(text_for_wordcloud)
            
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'Word Cloud for Artist Cluster {cluster_id}', fontsize=20)

            display_artists = ", ".join(artists_in_cluster[:5]) + (", ..." if len(artists_in_cluster) > 5 else "")
            plt.figtext(0.5, 0.05, f"Artists: {display_artists}", ha="center", fontsize=10, style='italic')

            filepath = output_dir / f'wordcloud_cluster_{cluster_id}.png'
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            plt.close()
        print(f"Cluster word clouds saved to {output_dir}")

    @staticmethod
    def plot_sentiment_arcs(artist_sentiment_data: dict, top_artists: list[str], output_path: Path):
        print("Plotting sentiment arcs for top artists...")
        plt.figure(figsize=(15, 12))
        colors = plt.get_cmap('tab10').colors

        # 绘制所有歌手句子的散点作为背景
        all_sentiments = [item for sublist in artist_sentiment_data.values() for item in sublist]
        if all_sentiments:
            all_x, all_y = zip(*all_sentiments)
            plt.scatter(all_x, all_y, alpha=0.03, color='gray', label='All Sentence Sentiments')

        # 为每个歌手绘制平滑趋势线
        for i, artist in enumerate(top_artists):
            if artist in artist_sentiment_data and len(artist_sentiment_data[artist]) > 10:
                x, y = zip(*artist_sentiment_data[artist])
                smoothed = lowess(y, x, frac=0.6, it=0)
                plt.plot(smoothed[:, 0], smoothed[:, 1], linewidth=3.5, color=colors[i % len(colors)], label=f'{artist} (Trend)')

        plt.title("Sentiment Arc Analysis for Top Artists", fontsize=20)
        plt.xlabel("Normalized Position in Song (Start -> End)", fontsize=12)
        plt.ylabel("Sentiment (0: Negative -> 1: Positive)", fontsize=12)
        plt.legend(fontsize=12, loc='best')
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.ylim(-0.1, 1.1)
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Sentiment arc plot saved to {output_path}")

    @staticmethod
    def plot_sentiment_arcs_by_cluster(cluster_sentiment_data: dict, output_path: Path):
        print("Plotting sentiment arcs by artist cluster...")
        plt.figure(figsize=(15, 12))
        colors = plt.get_cmap('tab10').colors

        for i, (cluster_id, sentiment_tuples) in enumerate(cluster_sentiment_data.items()):
            if len(sentiment_tuples) > 50:
                x, y = zip(*sentiment_tuples)
                smoothed = lowess(y, x, frac=0.5, it=0)
                plt.plot(smoothed[:, 0], smoothed[:, 1], linewidth=3.5, color=colors[i % len(colors)], label=f'Cluster {cluster_id} Trend')

        plt.title("Sentiment Arc Analysis by Artist Cluster", fontsize=20)
        plt.xlabel("Normalized Position in Song (Start -> End)", fontsize=12)
        plt.ylabel("Sentiment (0: Negative -> 1: Positive)", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.ylim(-0.1, 1.1)
        
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Cluster sentiment arc analysis plot saved to {output_path}")

    @staticmethod
    def plot_word_frequencies(freq_data: dict, output_path: Path, top_n: int = 20):
        print(f"Plotting top {top_n} word frequencies...")

        plt.figure(figsize=[12,16])
        words_without, counts_without = zip(*freq_data['without_stopwords'])
        words_without, counts_without = list(reversed(words_without)), list(reversed(counts_without))
        plt.barh(words_without, counts_without, color='lightcoral')
        plt.title(f'Top {top_n} Word Frequencies', fontsize=14)
        plt.xlabel('Frequency')
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        
        print(f"Word frequency plot saved to {output_path}")

    @staticmethod
    def plot_lyric_metrics_distribution(df: pd.DataFrame, output_path: Path):
        print("Plotting distribution of lyric metrics...")
        
        metrics_to_plot = {
            'Lyric Length (total characters)': 'len',
            'Unique Word Count': 'unique_word_cnt',
            'Rare Word Count': 'rare_word_cnt'
        }
        
        fig, axes = plt.subplots(1, 3, figsize=(20, 6))
        fig.suptitle('Distribution of Lyric Metrics', fontsize=20, y=1.02)
        
        for i, (title, col) in enumerate(metrics_to_plot.items()):
            if col in df.columns:
                axes[i].hist(df[col], bins=50, color='seagreen', alpha=0.7)
                axes[i].set_title(title, fontsize=14)
                axes[i].set_xlabel('Value')
                axes[i].set_ylabel('Number of Songs')
                axes[i].grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Lyric metrics distribution plot saved to {output_path}")

    @staticmethod
    def plot_artist_vocabulary_rankings(ranked_data: dict, output_path: Path, top_n: int = 15):
        """将歌手词汇丰富度指标的排名可视化"""
        print(f"Plotting top {top_n} artists by vocabulary metrics...")
        if not ranked_data:
            return

        fig, axes = plt.subplots(2, 1, figsize=(12, 18))
        fig.suptitle('Artist Vocabulary Richness Rankings', fontsize=20, y=0.96)

        # 图1: 词汇多样性排名
        diversity_df = ranked_data['diversity'].head(top_n)
        axes[0].barh(diversity_df.index, diversity_df['lexical_diversity_ratio'], color='darkcyan')
        axes[0].set_title(f'Top {top_n} Artists by Lexical Diversity (Unique Words / Total Words)', fontsize=14)
        axes[0].set_xlabel('Ratio (Higher is more diverse)')
        axes[0].invert_yaxis()

        # 图2: 生僻词使用率排名
        rare_word_df = ranked_data['rare_words'].head(top_n)
        axes[1].barh(rare_word_df.index, rare_word_df['rare_word_rate'], color='purple')
        axes[1].set_title(f'Top {top_n} Artists by Rare Word Usage Rate', fontsize=14)
        axes[1].set_xlabel('Rate (Higher means more rare words)')
        axes[1].invert_yaxis()

        plt.tight_layout(rect=[0, 0, 1, 0.94])
        plt.savefig(output_path, dpi=150)
        plt.close()
        print(f"Artist vocabulary rankings plot saved to {output_path}")

def analyze_decade(df:pd.DataFrame):
    print("\n--- Starting Decade-based Analysis ---")
    Visualizer.plot_wordclouds_by_decade(df, Config.WORDCLOUD_DIR)
    Visualizer.plot_topic_by_decade(df, Config.OUTPUT_DIR)

def analyze_artist(df:pd.DataFrame):
    print("\n--- Starting Artist-based Analysis ---")
    artist_analyzer = ArtistAnalyzer(df)

    # 基于歌词主题对歌手进行聚类
    artist_clusters_df = artist_analyzer.cluster_artists(Config.ARTIST_CLUSTER_COUNT)
    
    if artist_clusters_df is not None:
        with open("result/singer_cluster_.csv", "w") as f:
            print(artist_clusters_df.to_csv(), file=f)
        # 可视化歌手聚类结果
        Visualizer.plot_artist_clusters(artist_clusters_df, Config.OUTPUT_DIR / "artist_cluster_visualization.png")
        # 不同聚类歌手的词云图
        Visualizer.plot_wordclouds_by_cluster(df, artist_clusters_df, Config.WORDCLOUD_DIR)

    # 歌手特征词分析及可视化
    artist_analyzer.extract_characteristic_words(Config.OUTPUT_DIR / "artist_characteristic_words.json")

    # 不同聚类歌手的情感走向分析与可视化
    cluster_sentiment_data = artist_analyzer.analyze_sentiment_by_cluster(df, artist_clusters_df)
    Visualizer.plot_sentiment_arcs_by_cluster(cluster_sentiment_data, Config.OUTPUT_DIR / "sentiment_arc_analysis_by_cluster.png")

    sentiment_data = artist_analyzer.get_sentiment_data_for_plotting()
    Visualizer.plot_sentiment_arcs(sentiment_data, artist_analyzer.top_artists, Config.OUTPUT_DIR / "sentiment_arc_analysis.png")

def analyze_lyric(df:pd.DataFrame):
    print("\n--- Starting Lyric Characteristic Analysis ---")
    lyric_analyzer = LyricAnalyzer(df)
    artist_analyzer = ArtistAnalyzer(df)

    # 1. 词频分析与可视化
    freq_data = lyric_analyzer.calculate_word_frequencies()
    Visualizer.plot_word_frequencies(freq_data, Config.OUTPUT_DIR / "word_frequencies.png")
    
    # 2. 歌词指标分析与可视化
    df_with_metrics = lyric_analyzer.analyze_lyric_metrics()
    Visualizer.plot_lyric_metrics_distribution(df_with_metrics, Config.OUTPUT_DIR / "lyric_metrics_distribution.png")

    # 3. ...
    vocabulary_rankings = artist_analyzer.analyze_vocabulary_richness()
    Visualizer.plot_artist_vocabulary_rankings(vocabulary_rankings, Config.OUTPUT_DIR / "artist_vocabulary_rankings.png")

def main():
    # 环境设置
    Config.setup_environment()
    
    # 加载、处理数据
    print("Loading and preprocessing data...")
    df = pd.read_csv(Config.DATASET_PATH)   
    df["decade"] = pd.cut(df["release_year"], bins=Config.DECADE_BINS, labels=Config.DECADE_LABELS, right=False)
    df.dropna(subset=["tokenized_lyric", "decade", "processed_lyric"], inplace=True)

    # 任务1: 基于LDA进行歌词聚类, 建模主题
    print("\n--- Starting Topic Modeling ---")
    topic_analyzer = TopicAnalyzer(df["tokenized_lyric"])
    topic_analyzer.train(Config.NUM_TOPICS, Config.LDA_PASSES)
    topic_analyzer.save_topics(Config.OUTPUT_DIR / "lda_topics.txt")
    
    topic_dists = [topic_analyzer.get_doc_topic_dist(doc) for doc in tqdm(df["tokenized_lyric"], desc="Getting Topics")]
    topic_df = pd.DataFrame(topic_dists, index=df.index, columns=[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)])
    df = pd.concat([df, topic_df], axis=1)

    # 任务2: 年代分析
    # analyze_decade(df)
    
    # 任务3: 歌手分析
    # analyze_artist(df)

    # 任务4: 歌词分析
    analyze_lyric(df)

if __name__ == "__main__":
    main()