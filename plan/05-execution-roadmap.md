# 05. 课程式分阶段执行路线

这份文档不是普通里程碑列表，而是你的开发主线地图。你可以把它理解成一门小型项目课的目录页。

## 总目标

最终做出一个能真实运行的 `智能行业情报分析师`：

- 能抓取行业资讯网站内容
- 能抽取杂乱 HTML 表格并结构化
- 能完成向量化入库和 RAG 查询
- 能通过 FastAPI 提供服务
- 能通过 MCP 暴露给外部 Agent
- 能自动生成日报

## 学习方式

每个阶段都按照同一套节奏走：

1. 先理解这一阶段要解决的业务问题
2. 再补当前阶段涉及的代码模块
3. 写完后立刻做阶段自测
4. 最后记录这一阶段你能在简历里怎么讲

## 阶段总览

### Phase 1：项目基础层

目标：
把项目从空目录搭成一个结构清楚、可启动、可扩展的 Python 后端工程。

你会完成：

- 项目目录初始化
- `pyproject.toml` 依赖管理
- `Settings` 配置系统
- `FastAPI` 入口和基础路由
- 数据目录初始化

涉及模块：

- `src/intel_analyst/main.py`
- `src/intel_analyst/core/config.py`
- `src/intel_analyst/core/logging.py`
- `src/intel_analyst/api/routes/health.py`
- `src/intel_analyst/storage/file_store.py`

阶段文档：

- `course/phase-01-foundation.md`

### Phase 2：采集与结构化层

目标：
把真实网页内容稳定抓下来，并整理成后续 RAG 能消费的结构化数据。

你会完成：

- 站点配置 Schema
- 配置加载器
- `requests` 抓取器
- `Selenium` 登录辅助
- `BeautifulSoup` 内容解析
- `Pandas.read_html()` 表格结构化
- 原始 HTML / 文章 JSON / CSV 文件落盘

涉及模块：

- `src/intel_analyst/schemas/source.py`
- `src/intel_analyst/crawlers/source_loader.py`
- `src/intel_analyst/crawlers/auth.py`
- `src/intel_analyst/crawlers/generic_news.py`
- `src/intel_analyst/processing/html_tables.py`
- `src/intel_analyst/storage/article_repository.py`

阶段文档：

- `course/phase-02-crawling-and-structuring.md`

### Phase 3：RAG 与知识层

目标：
把抓取后的资讯变成可检索、可问答的行业知识库。

你会完成：

- Embedding 工厂
- LLM 工厂
- Chroma 向量库接入
- 文章切分与元数据设计
- 入库服务
- 检索问答服务

涉及模块：

- `src/intel_analyst/rag/embeddings.py`
- `src/intel_analyst/rag/llm.py`
- `src/intel_analyst/rag/vector_store.py`
- `src/intel_analyst/rag/prompts.py`
- `src/intel_analyst/services/ingestion_service.py`
- `src/intel_analyst/services/query_service.py`

阶段文档：

- `course/phase-03-rag-and-indexing.md`

### Phase 4：接口与协作层

目标：
把内部能力真正变成可调用服务，而不是停留在脚本阶段。

你会完成：

- 抓取接口
- 查询接口
- 重建索引接口
- 日报接口
- MCP tools / resource

涉及模块：

- `src/intel_analyst/api/dependencies.py`
- `src/intel_analyst/api/router.py`
- `src/intel_analyst/api/routes/*.py`
- `src/intel_analyst/mcp/server.py`

阶段文档：

- `course/phase-04-api-and-mcp.md`

### Phase 5：日报与工程增强层

目标：
让项目从“能跑”升级到“更像一个真正的后端应用”。

你会完成：

- 日报 Prompt 和落盘
- 基础测试
- 日志和异常处理
- 增量抓取与多站点扩展思路
- 后续前端 / 定时任务 / 推送的扩展设计

涉及模块：

- `src/intel_analyst/services/report_service.py`
- `tests/`
- `README.md`
- `config/sources/`

阶段文档：

- `course/phase-05-reporting-and-hardening.md`

## 推荐推进节奏

- 第 1 天：完成 Phase 1
- 第 2 天：完成 Phase 2
- 第 3 天：完成 Phase 3
- 第 4 天：完成 Phase 4
- 第 5 天：完成 Phase 5，并整理项目说明

如果你是边学边做，可以把每个阶段拆成两天，重点是每做完一层就能讲清楚“为什么这样设计”。

## 每阶段都要留下的产出

- 一份可运行代码
- 一次自测记录
- 一段简历项目描述素材
- 一份“我遇到了什么坑，如何解决”的笔记
