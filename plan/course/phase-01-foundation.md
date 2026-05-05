# Phase 1：项目基础层

## 这一阶段你要做出什么

目标不是做 AI，而是先把工程地基打稳。完成后，你应该能做到：

- 项目可以被 Python 正常识别和启动
- 有统一配置入口
- 有最基础的 FastAPI 服务
- 有本地数据目录初始化逻辑
- 有一个健康检查接口可用于确认服务正常

## 为什么先做这一层

很多项目一上来就写爬虫和模型调用，最后最容易乱在：

- 环境变量散落
- 路由和业务逻辑耦合
- 文件路径写死
- 本地能跑，换台机器就炸

先把这一层做好，后面每个模块都能往统一结构里接。

## 这一阶段涉及的文件

- `pyproject.toml`
- `src/intel_analyst/__init__.py`
- `src/intel_analyst/main.py`
- `src/intel_analyst/core/config.py`
- `src/intel_analyst/core/logging.py`
- `src/intel_analyst/api/router.py`
- `src/intel_analyst/api/routes/health.py`
- `src/intel_analyst/storage/file_store.py`
- `.env.example`

## 手把手实现顺序

### Step 1：先把项目变成 Python 包

你要做的事：

- 创建 `src/intel_analyst/`
- 放一个空的 `__init__.py`
- 在 `pyproject.toml` 里声明项目名、Python 版本和依赖

你现在的代码对应位置：

- `src/intel_analyst/__init__.py`
- `pyproject.toml`

验收：

- `python -m compileall src` 不报包结构错误

### Step 2：建立统一配置系统

你要做的事：

- 使用 `pydantic-settings` 管理环境变量
- 统一定义 `root_dir / data_dir / vectorstore_dir`
- 把模型供应商和 Embedding 配置也提前留好

你现在的代码对应位置：

- `src/intel_analyst/core/config.py`

重点理解：

- 为什么不能把目录字符串散写在各个模块里
- 为什么 `get_settings()` 要加缓存

验收：

- 在任何模块里都能通过 `get_settings()` 读到同一套配置

### Step 3：建立日志与目录初始化

你要做的事：

- 建一个简单日志配置
- 在应用启动时自动创建 `data/` 下的子目录

你现在的代码对应位置：

- `src/intel_analyst/core/logging.py`
- `src/intel_analyst/storage/file_store.py`
- `src/intel_analyst/main.py`

验收：

- 启动应用后，`data/raw`、`data/processed`、`data/tables`、`data/reports`、`data/vectorstore` 会自动出现

### Step 4：搭好 FastAPI 入口

你要做的事：

- 写 `create_app()`
- 注册统一路由
- 使用 `lifespan` 在启动时做初始化

你现在的代码对应位置：

- `src/intel_analyst/main.py`
- `src/intel_analyst/api/router.py`

重点理解：

- 为什么用工厂函数 `create_app()` 而不是直接堆全局逻辑
- 为什么把启动逻辑放进 `lifespan`

验收：

- `uvicorn intel_analyst.main:app --reload --app-dir src` 能启动服务

### Step 5：先做一个健康检查接口

你要做的事：

- 增加 `GET /api/v1/health`
- 返回基础状态和核心目录信息

你现在的代码对应位置：

- `src/intel_analyst/api/routes/health.py`

验收：

- 浏览器或接口工具访问后能返回 `status=ok`

## 这一阶段结束时，你应该能讲出来的话

- “我先搭了统一配置和目录初始化，避免后面爬虫和 RAG 模块各自管理路径。”
- “FastAPI 用工厂函数和 lifespan 管理启动行为，后续加数据库或缓存也容易扩展。”

## 常见坑

- `pythonpath` 没配好，导致 `intel_analyst` 导入失败
- `.env` 变量名和 `env_prefix` 对不上
- 忘了在启动时创建数据目录，后面写文件直接报错

## 阶段验收清单

- 项目可以启动
- `health` 接口可访问
- 配置类可读环境变量
- 本地数据目录会自动创建
