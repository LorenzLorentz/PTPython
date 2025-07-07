### 1. 环境配置

您可以参考`requirements.txt`配置对应库

```bash
pip install -r requirements.txt
```

### 2. 爬虫部分

首先请进入`crawler`文件夹

您可以通过下面命令在前台启动爬虫

```python
python task.py
```

也可以通过`tmux.sh`脚本在后台启动爬虫

```bash
bash tmux.sh
```

可以通过命令查看后台

```bash
tmux attach-session -t crawler
```

爬虫爬到的文件处于`Data/Song`和`Data/Singer`中

### 3. 数据分析部分

首先请进入`analysis`文件夹

预处理脚本为 `python pre_process.py`, 它会调用您爬取的文件

亦可直接运行 `python task.py`, 它内置了预处理逻辑, 并会开启数据分析任务 (同理可以调用`tmux.sh`脚本在后台启动)

数据分析结果呈现在 `result` 文件夹中