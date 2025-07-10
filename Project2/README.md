# Python PA2 - Online Judge System 

## 🎯 项目概述

这是 Python 课程 PA2 作业的仓库。

### 作业要求

详见文档 <https://keg-course.github.io/python-docs/oj/>

## 📁 仓库结构

```
.
├── app/                    # 主应用代码
│   ├── __init__.py
│   └── main.py            # FastAPI 应用入口（简单欢迎页面）
├── tests/                 # 测试用例
│   ├── conftest.py        # pytest 配置
│   ├── test_helpers.py    # 测试辅助函数
│   ├── test_api_*.py      # 各模块 API 测试
│   └── ...
├── .gitlab-ci.yml         # CI/CD 配置
├── requirements.txt       # Python 依赖
└── README.md             # 本文件
```

## 🧪 如何运行测试

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行所有测试
```bash
# 运行全部测试
python -m pytest tests/ -v

# 运行指定模块测试
python -m pytest tests/test_api_problems.py -v

# 运行单个测试
python -m pytest tests/test_api_problems.py::test_add_problem -v
```

### 3. 测试输出说明
- ✅ **PASSED** - 测试通过
- ❌ **FAILED** - 测试失败，需要实现相应功能
- 测试会检查你的 API 是否符合规范

## 🚀 如何启动应用

```bash
# 启动开发服务器
uvicorn app.main:app --reload

# 访问应用
# http://localhost:8000 - 主页面
# http://localhost:8000/docs - API 文档
```

## 🔄 CI/CD 说明

### 什么是 CI？
**CI (Continuous Integration)** 是持续集成，每当你提交代码到 GitLab 时，系统会自动：

1. **拉取你的代码**
2. **安装依赖** (`pip install -r requirements.txt`)
3. **运行测试** (`pytest tests/ -v`)
4. **显示结果** - 通过/失败

### CI 的好处
- ✅ **自动检测错误** - 提交后立即知道代码是否有问题
- ✅ **确保代码质量** - 所有功能都有测试覆盖
- ✅ **团队协作** - 防止提交破坏项目的代码
- ✅ **快速反馈** - 不用本地跑测试，推送后就能看结果

### 查看 CI 结果
1. 在 GitLab 项目页面点击 **"CI/CD" → "Pipelines"**
2. 看到 ✅ 绿色表示测试通过
3. 看到 ❌ 红色表示测试失败，点击查看详细错误

## 📝 开发建议

### 开发流程
1. **理解测试** - 先看 `tests/` 目录了解需要实现什么
2. **实现功能** - 在 `app/` 目录编写代码
3. **本地测试** - 运行 `pytest tests/ -v` 检查
4. **提交代码** - `git add . && git commit -m "实现XX功能"`
5. **推送验证** - `git push` 后查看 CI 结果

### 测试驱动开发
- 先看失败的测试，理解需要实现什么功能
- 实现最小可行的代码让测试通过
- 逐步完善功能，确保所有测试都通过

## 📚 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [pytest 测试框架](https://docs.pytest.org/)
- [GitLab CI/CD 文档](https://docs.gitlab.com/ee/ci/)

## ❓ 常见问题

**Q: 测试失败怎么办？**
A: 查看测试输出的错误信息，根据提示实现相应功能。

**Q: CI 一直失败？**
A: 检查 `.gitlab-ci.yml` 文件，确保依赖正确安装。

**Q: 如何调试测试？**
A: 使用 `pytest tests/test_xxx.py::test_function -v -s` 运行单个测试并显示输出。

---

**开始你的 OJ 系统开发之旅吧！** 🚀
