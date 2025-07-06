## **Python编程实验报告: 音乐数据爬虫与信息检索系统**

**复现与运行项目相关请见`README.md`**

### 1. 爬虫

#### 1.1 歌曲信息爬虫

通过`F12`分析歌曲页面的网络请求, 我们发现核心数据并非直接渲染在HTML中, 而是通过异步API(`Fetch/XHR`)加载.

翻阅`Fetch/XHR`中的请求, 我们识别出三个关键的请求:

- `.../song/detail`: 获取歌曲的详细信息(名称、歌手、专辑、封面图URL等).
- `.../song/lyric`: 获取歌曲的歌词.
- `.../comment/...`: 获取歌曲的评论.

![alt text](figs/request_comments.png)
![alt text](figs/request_detail.png)
![alt text](figs/request_lyric.png)

观察请求, 我们发现这些API均为**POST**请求, 其Payload包含两个关键参数: `params` 和 `encSecKey`; 并且, 显而易见的是, 这两个参数的值是经过加密的.

![alt text](figs/headers_detail.png)

![alt text](figs/payload_detail.png)

通过对请求的Initiator的JS源码进行追溯和调试,我们定位到了加密函数. 该函数将原始的、明文的请求参数(一个`dict`)作为输入, 经过一系列复杂的RSA和AES加密算法, 生成`params`和`encSecKey`. 我们在Python中复现了此加密过程,从而能够模拟合法的客户端请求,成功获取API返回的JSON数据.

![alt text](figs/encrypt.png)

为提高效率并避免对服务器造成过大压力, 我们设计了缓存机制. 在一次会话中, 对于同一个ID的请求,其结果会被缓存在内存中(如字典 `self.song_detail_cache`), 避免重复网络I/O. 核心数据获取函数 `_get_song_data` 也加入了重试与延时机制,以增强爬虫的鲁棒性.

```python
def _get_song_data(self, url:str, payload:dict) -> dict:
    # 加密逻辑
    encrypted_data = encrypt(payload)
    # 带重试的请求逻辑(忽略重试相关逻辑)
    res = requests.post(url, data=encrypted_data, headers=self.headers)
    # 忽略缓存逻辑
    return res.json()

def get_song_detail(self, song_id:str):
    if song_id not in self.song_detail_cache:
        # 构造payload并发起请求(忽略payload具体内容)
        self.song_detail_cache[song_id] = self._get_song_data(url=url, payload=payload)
    return self.song_detail_cache[song_id]

# 其他数据提取函数, 如get_song_name, get_song_lyric等
```

#### 1.2 歌手信息爬虫

与歌曲信息不同,歌手的主页信息(如简介、头像)直接嵌入在页面的HTML中. 因此, 我们采用了更直接的爬取策略:

我们直接向歌手主页URL(如 `https://music.163.com/artist?id={singer_id}`)发送**GET**请求, 获取页面完整的HTML文本.

然后使用正则表达式从HTML中匹配和提取所需信息. 例如, 歌手简介位于`<meta name="description" ...>`标签中.

```python
def _get_singer_data(self, singer_id:str) -> str:
    # 同样设计了缓存机制
    url = f"https://music.163.com/artist?id={singer_id}"
    return requests.get(url=url, headers=self.headers).text

def get_singer_profile(self, singer_id:str) -> str:
    html_content = self._get_singer_data(singer_id)
    pattern = r'<meta name="description" content="(.*?)" />'
    match = re.search(pattern, html_content)
    return match.group(1) if match else None

def get_singer_songs(self, singer_id:str) -> list[tuple[str, str]]:
    html_content = self._get_singer_data(singer_id)
    pattern = r'<li><a href="/song\?id=(\d+)">(.*?)</a></li>'
    return re.findall(pattern, html_content)

# 其他数据提取函数
```

#### 1.3 爬取策略与数据存储

为确保数据的相关性和代表性, 我们没有采用连续ID遍历的策略, 而是选择了自顶向下、从歌手到歌曲的方法:

我首先手动整理一份包含100位华语乐坛知名歌手的ID列表作为爬取的起点, 然后还整合了网易云热门歌手页面top请求中的著名歌手的信息.

![alt text](figs/top_singers.png)

![alt text](figs/request_top.png)

**爬取流程**:

- 遍历歌手ID列表,调用歌手爬虫获取每位歌手的基本信息和其热门50首歌曲列表.

- 再遍历获取到的歌曲列表,调用歌曲爬虫获取每首歌的详细信息(歌词、评论等).

- 其中用到前述的缓存逻辑来优化网络IO

最后, 我使用`@dataclasses.dataclass`定义`SongInfo`和`SingerInfo`两个类, 用于规整地组织采集到的数据. 这种方式不仅使代码更清晰(使用`.`调用时代码提示更方便), 也便于后续的序列化操作. 每个对象实例都保存为一个独立的JSON文件, 封面图片也一并下载至本地.

```python
@dataclasses.dataclass
class SongInfo:
    # (字段定义)
    def save(self):
        # 保存JSON和图片文件

@dataclasses.dataclass
class SingerInfo:
    # ... (字段定义)
    def save(self):
        # 保存为JSON和图片文件
```

<div STYLE="page-break-after: always;"></div>

### 2. WEB

我们基于Django框架, 构建了一个功能完备的音乐信息检索网站.

一个典型的Django网站的架构是这样的:

```
manage.py

(apps)
web_page - views.py (后端交互)
         - urls.py (路由匹配)
         - model.py (数据库)
         - templates/web_page.html (前端模版)
```

- **`Model`**: 我们设计了`Singer`, `Song`, `Comment`三个模型,它们与数据库表一一对应. 通过`ForeignKey`字段, 我们清晰地定义了模型间的层级关系(一个歌手有多首歌曲,一首歌曲有多条评论). 然后通过我们的`import_data.py`程序将爬取到的JSON数据载入SQLite数据库中.

```python
class Singer(models.Model):
    name = models.CharField(max_length=100)
    profile = models.TextField()
    # ...

class Song(models.Model):
    name = models.CharField(max_length=200)
    lyric = models.TextField()
    # ...
    singer = models.ForeignKey(Singer, on_delete=models.CASCADE)
```

- **`View`**: `views.py`是后端处理网络请求的核心, 涉及以下功能模块:

    - **主页**: 随机推荐若干首歌曲进行展示.
    
    - **搜索**: 接收前端传来的搜索关键字,使用Django ORM的查询API(如 `Song.objects.filter(name__icontains=keyword)`)进行模糊查询,支持对歌曲名和歌手名的搜索.
    
    - **分页**: 对搜索结果或歌手的歌曲列表进行分页处理,优化用户体验.
    
    - **详情页**: 根据传入的ID,查询并展示单首歌曲或单个歌手的完整信息.

- **`Template`**: 我们使用使用Django模板语言(这种语言带有python支持, 可以实现简单的程序) 编写HTML页面. 模板负责接收从视图传递过来的数据(`Context`), 并将其动态渲染成用户最终看到的网页. 我们设计了包括主页、搜索结果页、歌曲详情页和歌手详情页在内的多个模板.

整个网络结构大体遵循这样的**逻辑流程**:

用户请求URL -\> Django的`urls.py`进行路由匹配 -\> 调用`views.py`中对应的函数 -\> 与`Model`交互, 从数据库查询数据 -\> 将数据传递给`Template` -\> 模板引擎渲染HTML页面 -\> 返回给用户浏览器.

具体来说, 我实现了这些页面:

- 主页(导航页) 包括随机的歌曲推荐和随机的歌手推荐

![alt text](figs/page_nav.png) 

- 所有歌手页

![alt text](figs/page_all_singers.png) 

- 所有歌曲页

![alt text](figs/page_all_songs.png) 

- 歌手详情页(包括同一歌手的歌曲推荐和随机歌手推荐)

![alt text](figs/page_singer.png) 

- 歌曲详情页(包括歌词与评论, 包括同一歌手的歌曲推荐和随机歌曲推荐)

![alt text](figs/page_song.png)

- 搜索页

![alt text](figs/page_search.png) 

其他方面,

- 分页显示

![alt text](figs/item_pagenation.png) 

- 搜索栏

![alt text](figs/item_search.png)

- 评论区

![alt text](figs/item_comment.png) 

<div STYLE="page-break-after: always;"></div>

### 3. 数据分析与可视化

#### 3.1 数据预处理

我们首先去除了作词人、编曲、时长等歌词中与内容无关的信息, 然后借助停用词表和`jieba`库进行了分词并去除了非常常见的、与语义表达无关的词.

我们还记录了部分可能用到的信息, 比如歌词长度、独特的词的数量, 这对对歌手的分析会有帮助.

```python
words = [word for word in jieba.lcut(lyric) if word.strip() and word not in STOPWORDS and len(word) > 1]
tokenized_lyric = " ".join(words)

# (省略部分逻辑)

return {
    "processed_lyric": lyric,
    "tokenized_lyric": tokenized_lyric,
    "len": len(lyric),
    "unique_word_cnt": unique_word_cnt,
    "tot_word_cnt": tot_word_cnt
}
```

#### 3.2 基于LDA进行聚类与歌词主题建模

我们建立这样一个LDA模型:

```python
LdaMulticore(
    corpus=self.corpus, # self.corpus = [self.dictionary.doc2bow(doc) for doc in self.documents]
    id2word=self.dictionary, # self.dictionary.filter_extremes(no_below=15, no_above=0.5, keep_n=100000)
    num_topics=num_topics, # NUM_TOPICS=10
    passes=passes, # PASSES=10
    workers=os.cpu_count() - 1 or 1,
)
```

最终获得的主题为:

```txt
Topic: 1
Words: 0.013*"菩萨" + 0.012*"世界" + 0.011*"da" + 0.009*"Love" + 0.008*"天天" + 0.007*"所有" + 0.007*"有人" + 0.006*"不是" + 0.006*"努力" + 0.005*"ya" + 0.005*"一起" + 0.005*"永远" + 0.004*"Baby" + 0.004*"be" + 0.004*"感觉"

Topic: 2
Words: 0.013*"寂寞" + 0.010*"幸福" + 0.009*"真的" + 0.006*"la" + 0.006*"一生" + 0.006*"OH" + 0.005*"就算" + 0.005*"不再" + 0.005*"自由" + 0.004*"所有" + 0.004*"心中" + 0.004*"是否" + 0.004*"ha" + 0.004*"我爱你" + 0.004*"知道"

Topic: 3
Words: 0.013*"Oh" + 0.011*"不能" + 0.010*"知道" + 0.009*"现在" + 0.007*"心中" + 0.007*"我要" + 0.006*"Yeah" + 0.006*"快乐" + 0.005*"不会" + 0.005*"曾经" + 0.005*"世界" + 0.005*"na" + 0.005*"是否" + 0.005*"总是" + 0.005*"地方"

Topic: 4
Words: 0.030*"不要" + 0.007*"快乐" + 0.007*"知道" + 0.007*"我会" + 0.006*"幸福" + 0.006*"也许" + 0.006*"心里" + 0.006*"时间" + 0.005*"已经" + 0.004*"不会" + 0.004*"祝福" + 0.004*"故事" + 0.004*"想要" + 0.004*"永远" + 0.004*"感觉"

Topic: 5
Words: 0.017*"love" + 0.010*"La" + 0.009*"不会" + 0.008*"慢慢" + 0.008*"想念" + 0.008*"随风" + 0.007*"思念" + 0.007*"一起" + 0.005*"天空" + 0.005*"今天" + 0.005*"世界" + 0.005*"my" + 0.005*"My" + 0.004*"跟着" + 0.004*"一声"

Topic: 6
Words: 0.013*"知道" + 0.007*"离开" + 0.006*"明白" + 0.006*"不会" + 0.005*"世界" + 0.005*"回来" + 0.005*"时间" + 0.005*"不能" + 0.005*"不想" + 0.005*"想要" + 0.005*"眼泪" + 0.005*"回忆" + 0.004*"不是" + 0.004*"已经" + 0.004*"等待"

Topic: 7
Words: 0.007*"世界" + 0.006*"等待" + 0.005*"不想" + 0.005*"未来" + 0.004*"梦想" + 0.004*"青春" + 0.004*"希望" + 0.004*"喜欢" + 0.004*"不是" + 0.004*"永远" + 0.004*"月亮" + 0.004*"生活" + 0.004*"现在" + 0.004*"远方" + 0.003*"地方"

Topic: 8
Words: 0.014*"一天" + 0.009*"世界" + 0.008*"一生" + 0.008*"我要" + 0.007*"永远" + 0.007*"oh" + 0.007*"感觉" + 0.007*"Baby" + 0.006*"相信" + 0.005*"生命" + 0.005*"女人" + 0.005*"心中" + 0.005*"岁月" + 0.005*"未来" + 0.004*"无法"

Topic: 9
Words: 0.010*"爱情" + 0.008*"一起" + 0.007*"最后" + 0.007*"回忆" + 0.007*"世界" + 0.006*"不会" + 0.005*"永远" + 0.005*"曾经" + 0.005*"温柔" + 0.005*"朋友" + 0.005*"快乐" + 0.005*"不再" + 0.005*"所有" + 0.005*"相信" + 0.005*"记得"

Topic: 10
Words: 0.056*"you" + 0.032*"the" + 0.029*"me" + 0.022*"it" + 0.020*"to" + 0.020*"my" + 0.012*"in" + 0.012*"that" + 0.011*"know" + 0.011*"You" + 0.011*"love" + 0.011*"oh" + 0.010*"your" + 0.010*"and" + 0.010*"be"
```

#### 3.3 年代分析

1. 不同年代的主题变迁

![alt text](figs/decade_topic_dist.png)

观察这个图, 我们可以发现:

话题2和话题4轻微下降. 话题2的关键词是“寂寞”、“幸福”、“真的”、“一生”、“我爱你”. 这是非常典型的情歌主题. 话题4的关键词则是“不要”、“快乐”、“幸福”、“祝福”、“故事”, 构成了典型的分手或告别场景——虽然痛苦, 但仍给予对方祝福. 这两类主题是华语乐坛的传统优势项目, 它们比例的下降可能是由于其他品类的崛起; 又或者新曲式降低了人们对苦情歌的依赖.

话题7明显下降: 关键词是“世界”、“未来”、“梦想”、“青春”、“希望”、“月亮”、“远方”等等充满理想主义和浪漫色彩的主题. 这是从集体主义、英雄主义的叙事到个人主义的转变.

话题8 9明显上升. 话题8的关键词是“一天”、“一生”、“我要”、“永远”、“感觉”、“生命”、“女人”. 非常强调“我”的存在和意愿, 充满了个人感受. 而话题9的关键词是“爱情”、“一起”、“最后”、“回忆”、“朋友”、“温柔”. 相比于纯粹的苦情, 这个主题更加综合而温和. 这印证了个体意识的觉醒, 情感叙事的深化(不再是单纯的苦情或者宏大叙事).

话题1 3 5的含量相对稳定, 且一直较高. 话题1的关键词有“努力”, “天天”, “菩萨”. 整体上说应该是侧重奋斗与感悟的主题, 话题3的关键词有“不能”, “知道”, “是否”, 这些都是与内心挣扎与困惑相关的主题词汇. 话题5的关键词有“慢慢”、“随风”、“天空”, “想念”和“思念”, 这些词是更持久、更普遍的思念, 是滤掉痛苦之后深沉的回忆. 综上: 这三个主题是永恒的, 因此始终在华语歌曲中占有重要地位.

2. 不同年代的词云图

![alt text](figs/wordcloud_1980s.png)
![alt text](figs/wordcloud_1990s.png) 
![alt text](figs/wordcloud_2000s.png) 
![alt text](figs/wordcloud_2010s.png) 
![alt text](figs/wordcloud_2020s.png) 

#### 3.4 歌手分析

1. 歌手聚类

我们借助歌曲的主题建模, 可以知晓不同歌手的歌曲的主题倾向, 可以基于此对歌手进行聚类分析.

![alt text](figs/artist_cluster_visualization.png)

歌手被分为5类:

Cluster 0是是数量最大的群体, 代表了华语流行音乐最核心、最主流的歌词主题, 是芭乐的典型代表. 比如说蔡依林, 萧亚轩, 五月天, 汪苏泷.

Cluster 2的歌手在歌词上表现出的主题更为宏大、深远, 富含文化意象和人文关怀. 比如里面有许多充满中国风的歌手, 许多摇滚歌手, 许多充满异域风情的歌手.

Cluster 4 的歌手在歌词上更内省、更细腻, 更像诗歌或散文, 注重捕捉微妙的情绪和瞬间的感悟, 可能富含比喻、象征等修辞手法. 比如王菲, 陈绮贞, 陈珊妮等人.

Cluster 1 代表了更年轻、更直接、更具潮流感的主题, 比如鹿晗和华晨宇

Cluster 3 这个聚类非常清晰, 显著地与语言相关, 比如EXO, 比如Taylor Swift.

2. 不同聚类歌手的词云图

![alt text](figs/wordcloud_cluster_0.png) 
![alt text](figs/wordcloud_cluster_1.png) 
![alt text](figs/wordcloud_cluster_2.png) 
![alt text](figs/wordcloud_cluster_3.png) 
![alt text](figs/wordcloud_cluster_4.png)

我们可以注意到, 所有歌手的词云图中都醒目地出现了“世界”、“知道”、“不会”等词, 这类与人生思考、离别伤感的歌是华语歌曲永恒的主题.

Cluster 0 作为芭乐的代表, 其关键词会更偏向情歌.

CLuster 1 作为潮流的代表, 其关键词出现了许多英文词汇.

Cluster 2 作为更宏大的歌手的代表, 其里面有很多大词, 比如“我要”、“所有”.

Cluster 4 作为细腻派歌手的代表, 里面有很多小词和委婉的转折, 比如“感觉”、“或许”、“就算”.

3. 歌手歌词的情感变化

我们首先摘取了各个聚类的歌手做整体的情感变化分析:

在正向情感程度上: 宏大类(Cluster 2) > 芭乐类(Cluster 0) > 细腻类(Cluster 4) > 潮流类(Cluster 1) > 韩流类(Cluster 3)

![alt text](figs/sentiment_arc_analysis_by_cluster.png)

我们还可以在下图中看出不同歌手具体的情感走势, 可以明显看出王菲的歌曲的情感就明显更消极.

![alt text](figs/sentiment_arc_analysis.png)

#### 3.5 歌词具体分析

1. 词频统计

![alt text](figs/word_frequencies.png) 

2. 歌词长度, 独特单词数, 生僻单词数统计

![alt text](figs/lyric_metrics_distribution.png) 
![alt text](figs/artist_vocabulary_rankings.png)

#### 3.6 结论

<div STYLE="page-break-after: always;"></div>

### 4. 总结

#### 4.1 时间投入

- 爬虫模块: 约 **15小时**. 其中,纯粹的coding时间约5小时, 但大部分时间(约10+小时)用于分析网站请求、断点调试JavaScript以及攻克加密算法, 这是最具挑战性的部分.

- Web开发模块: 约 **15小时**. 从搭建最简单的框架到, 到编写前后端逻辑、设计数据库模型和CSS样式美化 ,此部分代码量最大, 工作最为繁琐.

- 数据分析模块: 约 **10小时**. 在数据准备就绪后,分析和可视化的过程相对流畅愉快. 期间遇到的主要问题是发现初期爬虫漏掉了 "发行时间" 字段, 需要返工补充数据. 还有就是有时候结论并不显著, 需要绞尽脑汁去对比分析.

(最近7天时间投入可视化 (未计入爬虫部分)) (源:wakatime)
![alt text](figs/wakatime.png)

#### 4.2 收获

本次大作业是一次极具价值的全栈实践. 通过这个项目, 我不仅系统地学习和应用了网络爬虫、后端开发和数据分析这三大现代软件工程中的技术, 这个过程极大地锻炼了我分析问题、解决问题以及项目工程化的能力. 特别是在研究反爬虫机制时, 虽然过程艰辛,但成功破解后的成就感是无与伦比的.

#### 4.3 建议

- 目前数据分析部分与Web系统是分离的. 未来可以将数据分析的结果(如词云图、分析报告)集成到Web前端, 作为一个板块进行展示, 让整个项目成为一个有机的整体.

- 可以为Web应用增加用户注册和登录功能. 记录用户的听歌、搜索行为, 结合已有的推荐算法, 为用户提供个性化的歌曲推荐服务.

**非常感谢老师和各位助教**设计了这次理论与实践紧密结合的作业, 让我受益匪浅.