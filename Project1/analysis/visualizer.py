import pandas as pd
from pathlib import Path
from tqdm import tqdm
import os

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from statsmodels.nonparametric.smoothers_lowess import lowess

from config import Config

class Visualizer:
    @staticmethod
    def plot_wordclouds_by_decade(df:pd.DataFrame, output_dir:Path):
        """为不同年代绘制词云图"""

        print("Generating word clouds by decade...")
        
        for decade in tqdm(df["decade"].unique(), desc="Plotting Decade Word Clouds"):
            # 获取该年代歌词
            decade_lyrics = " ".join(df[df["decade"] == decade]["tokenized_lyric"])
            
            # 绘制词云
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
        """绘制不同年代主题分布变化"""

        print("Plotting topic distribution across decades...")
        
        # 聚类同一年代主题分布
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
    def plot_singer_clusters(singer_clusters_df:pd.DataFrame, output_path:Path):
        """绘制歌手聚类"""
        
        print("Plotting artist clusters...")

        topic_cols = [col for col in singer_clusters_df.columns if col.startswith("Topic_")]
        
        # 计算聚类
        clusters = singer_clusters_df['cluster']
        clusters_unique = sorted(clusters.unique())

        # 使用主成分分析进行降维
        X = singer_clusters_df[topic_cols].values
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X)
        
        plt.figure(figsize=(16, 12))
        
        # 基于PCA绘制歌手聚类
        scatter = plt.scatter(X_pca[:,0], X_pca[:,1], c=clusters, cmap='tab10', s=100, alpha=0.7)
        for i, artist_name in enumerate(singer_clusters_df.index):
            plt.text(X_pca[i, 0], X_pca[i, 1] + 0.005, artist_name, ha='center', va='bottom', fontsize=9, alpha=0.8)
        
        plt.title('Artist Clusters based on Lyric Topics', fontsize=20)
        plt.xlabel('Principal Component 1', fontsize=12)
        plt.ylabel('Principal Component 2', fontsize=12)
        plt.legend(handles=scatter.legend_elements()[0], labels=[f"Cluster {c}" for c in clusters_unique], title="Clusters")
        plt.grid(True, linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(output_path, dpi=150)
        plt.close()

    @staticmethod
    def plot_wordclouds_by_cluster(df:pd.DataFrame, singers_clusters_df:pd.DataFrame, output_dir:Path):
        """为不同聚类歌手绘制词云图"""

        print("Generating word clouds by artist cluster...")
        
        for cluster_id in tqdm(sorted(singers_clusters_df['cluster'].unique()), desc="Plotting Cluster Word Clouds"):
            # 获取该聚类歌手歌词
            cluster_singers = singers_clusters_df[singers_clusters_df['cluster'] == cluster_id].index.tolist()
            cluster_lyric = " ".join(df[df['singer_name'].isin(cluster_singers)]['tokenized_lyric'].dropna())
            
            # 绘制词云图
            wordcloud = WordCloud(
                font_path=os.path.expanduser("~/.font/Arial Unicode.ttf"),
                width=1000, height=600, background_color='white',
                colormap='plasma'
            ).generate(cluster_lyric)
            
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis('off')
            plt.title(f'Word Cloud for Artist Cluster {cluster_id}', fontsize=20)

            # 标注聚类中的歌手
            display_singers = ", ".join(cluster_singers[:5]) + (", ..." if len(cluster_singers) > 5 else "")
            plt.figtext(0.5, 0.05, f"Artists: {display_singers}", ha="center", fontsize=10, style='italic')

            plt.savefig(output_dir / f'wordcloud_cluster_{cluster_id}.png', dpi=150, bbox_inches='tight')
            plt.close()

    @staticmethod
    def plot_sentiment_arcs(artist_sentiment_data: dict, top_artists: list[str], output_path: Path):
        """绘制(部分)歌手歌曲情感走向"""

        print("Plotting sentiment arcs for top artists...")
        
        plt.figure(figsize=(15, 12))
        colors = plt.get_cmap('tab10').colors

        # 绘制所有歌手句子的散点作为背景
        all_sentiments = [item for sublist in artist_sentiment_data.values() for item in sublist]
        if all_sentiments:
            all_x, all_y = zip(*all_sentiments)
            plt.scatter(all_x, all_y, alpha=0.03, color='gray', label='All Sentence Sentiments')

        # 为列表中每个歌手绘制平滑趋势线
        for i, artist in enumerate(top_artists):
            if artist in artist_sentiment_data and len(artist_sentiment_data[artist]) > 10:
                x, y = zip(*artist_sentiment_data[artist])
                smoothed = lowess(y, x, frac=0.6, it=0)
                plt.plot(smoothed[:, 0], smoothed[:, 1], linewidth=3.5, color=colors[i%len(colors)], label=f'{artist}')

        plt.title("Sentiment Arc Analysis for Top Artists", fontsize=20)
        plt.xlabel("Normalized Position in Song (Start -> End)", fontsize=12)
        plt.ylabel("Sentiment (0: Negative -> 1: Positive)", fontsize=12)
        plt.legend(fontsize=12, loc='best')
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.ylim(-0.1, 1.1)
        plt.savefig(output_path, dpi=150)
        plt.close()

    @staticmethod
    def plot_sentiment_arcs_by_cluster(cluster_sentiment_data:dict, output_path:Path):
        """绘制各个聚类歌手的歌曲情感走向"""

        print("Plotting sentiment arcs by artist cluster...")
        
        plt.figure(figsize=(15, 12))
        colors = plt.get_cmap('tab10').colors

        # 为不同聚类绘制平滑趋势线
        for i, (cluster_id, sentiment_tuples) in enumerate(cluster_sentiment_data.items()):
            if len(sentiment_tuples) > 50:
                x, y = zip(*sentiment_tuples)
                smoothed = lowess(y, x, frac=0.5, it=0)
                plt.plot(smoothed[:, 0], smoothed[:, 1], linewidth=3.5, color=colors[i%len(colors)], label=f'Cluster {cluster_id}')

        plt.title("Sentiment Arc Analysis by Artist Cluster", fontsize=20)
        plt.xlabel("Normalized Position in Song (Start -> End)", fontsize=12)
        plt.ylabel("Sentiment (0: Negative -> 1: Positive)", fontsize=12)
        plt.legend(fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.ylim(-0.1, 1.1)
        plt.savefig(output_path, dpi=150)
        plt.close()

    @staticmethod
    def plot_word_frequencies(freq_data:tuple, output_path:Path, top_n:int = 20):
        """绘制词频图"""

        print(f"Plotting top {top_n} word frequencies...")

        plt.figure(figsize=[12,16])
        words, counts = zip(*freq_data)
        plt.barh(list(reversed(words)), list(reversed(counts)), color='lightcoral')
        plt.title(f'Top {top_n} Word Frequencies')
        plt.xlabel("Frequency")
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()

    @staticmethod
    def plot_lyric_metrics_dist(df: pd.DataFrame, output_path: Path):
        """绘制歌词的各类统计量分布"""
        
        print("Plotting distribution of lyric metrics...")
        
        # 建立图例和index的对应关系
        metrics_to_plot = {
            "Lyric Length": "len",
            "Unique Word Count": "unique_word_cnt",
            "Rare Word Count": "rare_word_cnt"
        }
        
        fig, axes = plt.subplots(1, 3, figsize=(20, 8))
        fig.suptitle("Distribution of Lyric Metrics", fontsize=20)
        
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

    @staticmethod
    def plot_singer_vocab_rankings(ranked_data:dict, output_path:Path, top_n:int=10):
        """绘制歌手词汇丰富度指标的排名"""
        
        print(f"Plotting top {top_n} artists by vocabulary metrics...")

        fig, axes = plt.subplots(2, 1, figsize=(12, 18))
        fig.suptitle('Artist Vocabulary Richness Rankings', fontsize=20)

        # 词汇多样性排名
        diverse_word_df = ranked_data["diverse"].head(top_n)
        axes[0].barh(diverse_word_df.index, diverse_word_df['diverse_word_ratio'], color='darkcyan')
        axes[0].set_title(f'Top {top_n} Artists by Diverse Word Ratio', fontsize=14)
        axes[0].set_xlabel('Ratio')
        axes[0].invert_yaxis()

        # 生僻词使用率排名
        rare_word_df = ranked_data["rare"].head(top_n)
        axes[1].barh(rare_word_df.index, rare_word_df["rare_word_ratio"], color='purple')
        axes[1].set_title(f'Top {top_n} Artists by Rare Word Usage Rate', fontsize=14)
        axes[1].set_xlabel('Rate')
        axes[1].invert_yaxis()

        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()