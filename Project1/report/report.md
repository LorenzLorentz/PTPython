## **实验报告: 爬虫与信息系统**

王鹏杰 2024010860 计48-经42

**复现与运行项目相关请见`README.md`**

**分析结果请参见数据分析报告**

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

#### 1.4 实验结果

最终爬取了$136$位歌手和$6543$首歌.

<div STYLE="page-break-after: always;"></div>

### 2. WEB

我们基于Django框架, 构建了一个功能完备的音乐信息检索网站.

#### 2.1 框架设计

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

- **`Template`**: 我们使用使用Django模板语言(这种语言大体上和html相同, 但带有python支持, 可以实现简单的程序) 编写HTML页面. 模板负责接收从视图传递过来的数据(`Context`), 并将其动态渲染成用户最终看到的网页. 我们设计了包括主页、搜索结果页、歌曲详情页和歌手详情页在内的多个模板.

整个网络结构大体遵循这样的**逻辑流程**:

用户请求URL -\> Django的`urls.py`进行路由匹配 -\> 调用`views.py`中对应的函数 -\> 与`Model`交互, 从数据库查询数据 -\> 将数据传递给`Template` -\> 模板引擎渲染HTML页面 -\> 返回给用户浏览器.

#### 2.2 核心组件设计

- 数据组件

继承在data这个app的`views.py`中, 依托Sqlite的数据库功能, 实现了聚类, 查找等功能. 比如:

```python
# 过滤自身并随机查找
all_songs = singer.songs.exclude(id=song_id)
all_song_ids = list(all_songs.values_list("id", flat=True))
random_song_ids = random.sample(all_song_ids, min(len(all_song_ids), num))
song_list_same = all_songs.filter(id__in=random_song_ids)

# 关键词匹配
query_name = Q(name__icontains=query_singer)
query_profile = Q(profile__icontains=query_singer)
return Singer.objects.filter(query_name | query_profile)
```

- 分页控件

分页控件依赖django的Paginator, 我们首先需要根据结果和每页个数构造分页器, 然后根据页码获得实际页面对象.

```python
paginator = Paginator(results, 12)
page_obj = paginator.get_page(page_number)
```

为了显示翻页, 我们要在模版中用django特色的html语言实现处理逻辑

```html
{% if page_obj.has_previous %}
    <a href="?{{ prefix }}page=1" class="page-btn">首页</a>
    <a href="?{{ prefix }}page={{ page_obj.previous_page_number }}" class="page-btn">&laquo;上一页</a>
{% else %}
    <span class="page-btn disabled">首页</span>
    <span class="page-btn disabled">&laquo;上一页</span>
{% endif %}
```

- 搜索栏控件

搜索栏涉及到一个动态样式的控件, 我们首先需要用html勾勒他的完整样式, 如下涉及了搜索框、下拉栏、异常消息三个元素

```html
<div class="search-box-interactive">
    <!--略-->
    <input type="text" name="q" class="search-input-interactive" id="search-input" placeholder="搜索..." autocomplete="off" required>
</div>

<div id="search-error-message" style="color: whitesmoke; font-size: 14px; text-align: center; margin-top: 5px;"></div>

<div class="search-dropdown" id="search-dropdown">
    <ul class="dropdown-menu">
        <!--略-->
    </ul>
</div>
```

然后我们需要借助JavaScript脚本去捕获涉及到的元素, 处理对应的事件, 如.

```JavaScript
const searchInput = document.getElementById('search-input');
const searchDropdown = document.getElementById('search-dropdown');
// 略

// 1. 点击输入框时，显示/隐藏下拉菜单
searchInput.addEventListener('focus', function() {
    searchDropdown.classList.add('active');
    searchBox.classList.add('focused');
});

// 略
```

#### 2.3 页面设计

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

**注:分析结果请参见数据分析报告**

#### 3.1 数据预处理

我们首先去除了作词人、编曲、时长等歌词中与内容无关的信息, 然后借助停用词表和 **`jieba`库** 进行了分词并去除了非常常见的、与语义表达无关的词.

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

#### 3.2 整体数据处理架构

为了避免将所有计算、绘图和流程控制代码混杂在一起, 我采用了分层设计, 将整个框架解构成三个核心部分.

1. Analyzer

负责所有的核心计算、数据处理和模型训练. 它接收原始或半处理的数据, 输出结构化的分析结果.

比如 `TopicAnalyzer` 负责训练LDA模型, 并推断每首歌的主题分布.

```Python
class TopicAnalyzer:
    def __init__(self, tokenized_docs: list[str]):
        print("Initializing Topic Analyzer...")
        self.documents = [doc.split() for doc in tokenized_docs]
        self.dictionary = Dictionary(self.documents)
        self.corpus = [self.dictionary.doc2bow(doc) for doc in self.documents]
        self.model = None

    # 省略代码

    def get_doc_topic_dist(self, doc_tokens: str) -> list[float]:
        """获取单个文档的主题分布（纯数据）"""
        bow = self.dictionary.doc2bow(doc_tokens.split())
        dist = self.model.get_document_topics(bow, minimum_probability=0)
        return [prob for _, prob in dist]
```
2. Visualizer

负责将 Analyzer 生成的数据结果进行可视化呈现. 它接收结构化数据, 输出图表、词云等视觉元素. 由于只绘图, 不计算, Visualizer 的方法都是静态方法, 仅依赖于传入的参数来绘图.

如 `Visualizer.plot_topic_distribution_by_decade` 接收一个包含主题比例的 `DataFrame` 并将其绘制成图表.

```Python
class Visualizer:
    @staticmethod
    def plot_topic_distribution_by_decade(song_df: pd.DataFrame, output_path: Path):
        """接收数据，绘制不同年代的主题分布图"""
        print("Plotting topic distribution across decades...")
        # 仅包含绘图逻辑
        decade_topic_dist = song_df.groupby("decade")[[f"Topic_{i+1}" for i in range(Config.NUM_TOPICS)]].mean()
        decade_topic_dist.plot(kind="bar", stacked=True, figsize=(15, 8), ...)
        plt.title("Topic Distribution Across Decades")
        plt.savefig(output_path, dpi=150)
        plt.close()
```

3. analyze_***函数

负责编排一个完整的分析任务. 它调用 Analyzer 来执行计算, 然后将计算结果传递给 Visualizer 来进行绘图. 这使得主逻辑非常清晰, 易于理解一个完整分析任务的步骤.

如下面的`analyze_decade`函数

```Python
def analyze_decade(df: pd.DataFrame):
    """编排与年代相关的分析和可视化任务"""
    print("\n--- Starting Decade-based Analysis ---")
    # 任务1: 不同年代的词云图 (调用Visualizer)
    Visualizer.plot_wordclouds_by_decade(df, Config.WORDCLOUD_DIR)

    # 任务2: 不同年代的主题分布变化 (调用Visualizer)
    # 注意: 此处传入的df已经由之前的步骤计算好了主题分布
    Visualizer.plot_topic_distribution_by_decade(df, Config.OUTPUT_DIR / "decade_topic_distribution.png")
```

具体来说, 我用到了 `TopicAnalyzer, SingerAnalyzer, LyricAnalyzer` 三个 `Analyzer`, 涉及 wordcloud图等一系列 `Visualizer` 的方法, 还有 `analyze_decade, analyze_singer, analyze_lyric` 三个函数.

#### 3.3 基于LDA进行聚类与歌词主题建模

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

其中用到了 **gensim库**, 这是一个主要涉及机器学习和自然语言处理的python库.

然后我们可以将歌词按照主题分为10类, 这可以让我们更深刻、更快速地理解歌词的内核, 便于后续大规模分析.

#### 3.4 年代分析

1. 为了探究不同年代之间歌曲主题的变迁, 我绘制了不同年代不同主题的占比变化图

2. 为了探究不同年代的关键词, 我绘制了不同年代的词云图

此处和后文中的词云图均基于 **wordcloud库** 实现

#### 3.5 歌手分析

1. 我们首先基于之前得到的主题分类对歌手进行了聚类.

具体说, 由于每一首歌可以有10个主题上的分数, 我们取平均后便得到了一个歌手的10维向量表征, 然后我们就可以利用 **KMeans算法** 对歌手进行聚类分析. 为了可视化, 我们利用**PCA**(主成分分析)算法将10维向量投影到二维平面上, 然后对不同聚类进行染色, 执行可视化.

其中我们用到了 **scikit-learn 库**, 调用了其 KMeans 与 PCA 实现.

2. 然后我们对不同聚类的歌手也分别绘制了词云图, 来观察其语言特征.

3. 最后, 为了探究不同歌手的歌曲的情感走向, 我调用 **snownlp 库**, 它内置了一个基于贝叶斯模型的中文情感分类器, 可以为每个句子打一个情感分数. 我基于此绘制了不同歌手的歌曲情感走向, 不同聚类歌手的歌曲情感走向.

#### 3.6 歌词分析

1. 我首先做了最简单的词频分析, 绘制从高到低前20个常用词(已去除停用词)的词频分布;

2. 然后我考察更细节的统计量, 绘制了歌曲长度、歌曲中unique的词汇的数量、歌曲中rare(定义为在不超过5首歌中出现)的词汇数量的统计图.

3. 最后我考察了不同歌手的unique词汇和rare词汇的占比, 并绘制出各自的前十名.

4. 这里涉及到大量的聚合统计, 主要基于 **pandas库**完成的.

<div STYLE="page-break-after: always;"></div>

### 4. 总结

#### 4.1 时间投入

- 爬虫模块: 约 **15小时**. 其中纯粹的coding时间约5小时, 但大部分时间(约10小时)用于分析网站请求、断点调试JavaScript, 这是最具挑战性的部分.

- Web开发模块: 约 **20小时**. 从搭建简单的框架, 到编写前后端逻辑、设计数据库模型和CSS样式美化, 此部分代码量最大, 工作最为繁琐.

- 数据分析模块: 约 **10小时**. 在数据准备就绪后, 分析和可视化的过程相对流畅愉快. 期间遇到的主要问题是发现初期爬虫漏掉了 "发行时间" 字段, 需要返工补充数据. 还有就是有时候结论并不显著, 需要绞尽脑汁去对比分析.

(最近7天时间投入可视化 (未计入爬虫部分)) (源:wakatime)
![alt text](figs/wakatime.png)

#### 4.2 收获

本次大作业是一次极具价值的全栈实践. 通过这个项目, 我系统地学习和应用了网络爬虫、后端开发和数据分析这三大技术, 这个过程极大地锻炼了我分析问题、解决问题以及项目工程化的能力. 特别是在研究反爬虫机制时, 虽然过程艰辛,但成功破解后的成就感是无与伦比的.

#### 4.3 建议

- 目前数据分析部分与Web系统是分离的. 未来可以将数据分析的结果(如词云图、分析报告)集成到Web前端, 作为一个板块进行展示, 让整个项目成为一个有机的整体.

- 可以为Web应用增加用户注册和登录功能. 记录用户的听歌、搜索行为, 结合已有的推荐算法, 为用户提供个性化的歌曲推荐服务.

**非常感谢老师和各位助教**设计了这次理论与实践紧密结合的作业, 让我受益匪浅.