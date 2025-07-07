from pathlib import Path
import os

from gensim.models.ldamulticore import LdaMulticore
from gensim.corpora import Dictionary

class TopicAnalyzer:
    def __init__(self, tokenized_docs: list[str]):
        """构建文本和词袋"""
        
        print("Initializing Topic Analyzer...")
        self.documents = [doc.split() for doc in tokenized_docs]
        self.dictionary = Dictionary(self.documents)
        self.dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.documents]
        self.model = None

    def train(self, num_topics:int, passes:int) -> LdaMulticore:
        """按照指定参数基于构建的文本进行训练"""

        print(f"Training LDA model with {num_topics} topics...")
        self.model = LdaMulticore(
            corpus=self.corpus,
            id2word=self.dictionary,
            num_topics=num_topics,
            passes=passes,
            workers=os.cpu_count() - 1 or 1,
        )
        return self.model

    def get_doc_topic_dist(self, doc_tokens:str) -> list[float]:
        """获得文本的主题分布"""

        bow = self.dictionary.doc2bow(doc_tokens.split())
        dist = self.model.get_document_topics(bow, minimum_probability=0)
        return [prob for _, prob in dist]

    def save_topics(self, path:Path):
        """保存主题结果"""

        print(f"Saving topics to {path}...")
        with open(path, "w") as f:
            for idx, topic in self.model.print_topics(-1, num_words=15):
                f.write(f"Topic: {idx+1}\nWords: {topic}\n\n")