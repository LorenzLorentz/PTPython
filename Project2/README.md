# Python PA2 - Online Judge System 

## 项目概述

这是 Python 课程 PA2 作业的仓库。

### 作业要求

详见文档 <https://keg-course.github.io/python-docs/oj/>

## 仓库结构

```
.
├── app/                    # 主应用代码
│   ├── __init__.py
│   └── main.py            # FastAPI 应用入口
├── tests/                 # 测试用例
│   ├── conftest.py        # pytest 配置
│   ├── test_helpers.py    # 测试辅助函数
│   ├── test_api_*.py      # 各模块 API 测试
│   └── ...
├── .gitlab-ci.yml         # CI/CD 配置
├── requirements.txt       # Python 依赖
└── README.md             # 本文件
```

## 如何运行测试

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行测试
```bash
# 运行全部测试
python -m pytest tests/ -v

python -m pytest tests/test_api_submissions.py::test_get_submission_result -v
python -m pytest tests/test_api_logs.py::test_get_submission_log -v

# 运行指定模块测试
python -m pytest tests/test_api_problems.py -v

# 运行单个测试
python -m pytest tests/test_api_problems.py::test_add_problem -v
```

### 3. 测试结果
- **PASSED** - 测试通过
- **FAILED** - 测试失败，需要实现相应功能

## 如何启动应用

```bash
# 启动开发服务器
uvicorn app.main:app --reload

# 访问应用
# http://localhost:8000 - 主页面
# http://localhost:8000/docs - API 文档
```

## CI/CD 说明

### 什么是 CI？
CI (Continuous Integration) 持续集成，每次提交代码时系统会自动：

1. 拉取代码
2. 安装依赖 (`pip install -r requirements.txt`)
3. 运行测试 (`pytest tests/ -v`)
4. 显示结果

### CI 的作用
- 自动检测错误 - 提交后立即知道代码状态
- 保证代码质量 - 所有功能都有测试覆盖
- 便于团队协作 - 避免提交有问题的代码
- 快速反馈 - 无需本地测试，推送后即可查看结果

### 查看 CI 结果
1. 进入 GitLab 项目页面，点击 "CI/CD" → "Pipelines"
2. 绿色表示测试通过，红色表示失败
3. 点击失败的任务可以查看详细错误信息

## 开发建议

### 开发流程
1. **看测试** - 先查看 `tests/` 目录了解需要实现的功能
2. **写代码** - 在 `app/` 目录实现功能
3. **跑测试** - 运行 `pytest tests/ -v` 检查
4. **提交** - `git add . && git commit -m "实现XX功能"`
5. **推送** - `git push` 并查看 CI 结果

### 测试驱动开发
- 先看失败的测试，了解要实现什么
- 写最简单的代码让测试通过
- 逐步完善功能

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [pytest 测试框架](https://docs.pytest.org/)
- [GitLab CI/CD 文档](https://docs.gitlab.com/ee/ci/)

## 常见问题

**Q: 测试失败怎么办？**
A: 看测试输出的错误信息，按照提示实现对应功能。

**Q: CI 一直失败？**
A: 目前CI还没配置好，暂时不用管这个事情

**Q: 如何调试测试？**
A: 用 `python -m pytest tests/test_xxx.py::test_function -v -s` 运行单个测试查看详细输出。
