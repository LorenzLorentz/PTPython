import pandas as pd
from tqdm import tqdm

from topic_ana import TopicAnalyzer
from singer_ana import SingerAnalyzer
from lyric_ana import LyricAnalyzer
from visualizer import Visualizer
from config import Config

def analyze_decade(df:pd.DataFrame):
    """对年代特征进行分析与可视化"""
    
    print("\n--- Starting Decade-based Analysis ---")
    Visualizer.plot_wordclouds_by_decade(df, Config.WORDCLOUD_DIR)
    Visualizer.plot_topic_by_decade(df, Config.OUTPUT_DIR)

def analyze_artist(df:pd.DataFrame):
    """对歌手特征进行分析与可视化"""

    print("\n--- Starting Artist-based Analysis ---")
    singer_analyzer = SingerAnalyzer(df)

    # 基于歌词主题对歌手进行聚类
    singer_clusters_df = singer_analyzer.cluster_singers(Config.ARTIST_CLUSTER_COUNT)
    with open("result/singer_cluster_.csv", "w") as f:
        print(singer_clusters_df.to_csv(), file=f)
    
    # 可视化歌手聚类结果
    Visualizer.plot_singer_clusters(singer_clusters_df, Config.OUTPUT_DIR / "artist_cluster_visualization.png")
    
    # 不同聚类歌手的词云图
    Visualizer.plot_wordclouds_by_cluster(df, singer_clusters_df, Config.WORDCLOUD_DIR)

    # 歌手特征词分析
    singer_analyzer.extract_charac_words(Config.OUTPUT_DIR / "artist_characteristic_words.json")

    # 歌手词汇丰富度分析
    if not "rare_word_cnt" in df.columns:
        df = LyricAnalyzer().stat_rare_words()
    vocabulary_rankings = singer_analyzer.analyze_vocabulary_richness()
    Visualizer.plot_singer_vocab_rankings(vocabulary_rankings, Config.OUTPUT_DIR / "artist_vocabulary_rankings.png")

    # 不同聚类歌手的情感走向分析与可视化
    sentiment_data = singer_analyzer.get_sentiment()
    Visualizer.plot_sentiment_arcs(sentiment_data, singer_analyzer.top_singers, Config.OUTPUT_DIR / "sentiment_arc_analysis.png")
    cluster_sentiment_data = singer_analyzer.get_sentiment_by_cluster(df, singer_clusters_df)
    Visualizer.plot_sentiment_arcs_by_cluster(cluster_sentiment_data, Config.OUTPUT_DIR / "sentiment_arc_analysis_by_cluster.png")

def analyze_lyric(df:pd.DataFrame):
    print("\n--- Starting Lyric Characteristic Analysis ---")
    lyric_analyzer = LyricAnalyzer(df)
    df = lyric_analyzer.stat_rare_words()

    # 词频分析与可视化
    freq_data = lyric_analyzer.calc_word_freq()
    Visualizer.plot_word_frequencies(freq_data, Config.OUTPUT_DIR / "word_frequencies.png")
    
    # 歌词指标分析与可视化
    df = lyric_analyzer.stat_rare_words()
    Visualizer.plot_lyric_metrics_dist(df, Config.OUTPUT_DIR / "lyric_metrics_distribution.png")

def main():
    # 环境设置
    Config.setup_environment()
    
    # 加载、处理数据
    print("Loading and preprocessing data...")
    df = pd.read_csv(Config.DATASET_PATH)   
    df["decade"] = pd.cut(df["release_year"], bins=Config.DECADE_BINS, labels=Config.DECADE_LABELS, right=False)
    df.dropna(subset=["tokenized_lyric", "decade", "processed_lyric"], inplace=True)

    # 基于LDA进行歌词聚类, 建模主题
    print("\n--- Starting Topic Modeling ---")
    topic_analyzer = TopicAnalyzer(df["tokenized_lyric"])
    topic_analyzer.train(Config.NUM_TOPICS, Config.LDA_PASSES)
    topic_analyzer.save_topics(Config.OUTPUT_DIR / "lda_topics.txt")
    
    topic_dists = [topic_analyzer.get_doc_topic_dist(doc) for doc in tqdm(df["tokenized_lyric"], desc="Getting Topics")]
    topic_df = pd.DataFrame(topic_dists, index=df.index, columns=[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)])
    df = pd.concat([df, topic_df], axis=1)

    # 歌词分析
    analyze_lyric(df)

    # 年代分析
    analyze_decade(df)
    
    # 歌手分析
    analyze_artist(df)

if __name__ == "__main__":
    main()