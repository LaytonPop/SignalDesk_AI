# 02. 系统架构设计

## 1. 总体架构

```text
行业站点
   │
   ▼
[Crawler]
requests / Selenium
   │
   ▼
[Processing]
正文清洗 / Pandas.read_html / 表格结构化
   │
   ├─ 原始 HTML -> data/raw
   ├─ 结构化 JSON -> data/processed
   └─ CSV 表格 -> data/tables
   │
   ▼
[RAG Pipeline]
Chunking -> Embedding -> Chroma
   │
   ├─ FastAPI Query API
   ├─ FastAPI Daily Report API
   └─ MCP Tools / Resources
```

## 2. 技术选型

### Web / API

- `FastAPI`
原因：类型友好、接口文档自动生成、适合快速做 RESTful 服务

### 爬虫

- `requests + BeautifulSoup`
原因：适合列表页、公告页、常规详情页抓取

- `Selenium`
原因：适合需要登录、JS 渲染或反爬较轻的页面

### 结构化处理

- `Pandas.read_html()`
原因：可以直接把杂乱 HTML 表格转成 DataFrame，再导出 CSV / JSON

### RAG

- `LangChain`
原因：便于串接文本切分、Embedding、向量检索、Prompt 编排

- `Chroma`
原因：本地开发成本低，适合作为单机版简历项目的默认向量库

### LLM / Embedding

- 默认建议 `Ollama + Qwen` 做本地开源模型推理
- 默认建议 `HuggingFace Embeddings` 做本地向量化
- 同时保留 OpenAI-compatible 接口，方便后续切换

### MCP

- `mcp Python SDK`
原因：可以把查询、日报、抓取能力暴露为标准工具，体现项目先进性

## 3. 数据流说明

### 抓取流

1. 读取站点配置
2. 初始化 requests Session
3. 如需要，先登录
4. 抓取列表页并抽取详情页链接
5. 抓取详情页正文与表格
6. 存储原始 HTML 和结构化文章

### 入库流

1. 读取结构化文章
2. 将正文与表格摘要拼成统一知识文本
3. 文本切分
4. 生成向量
5. 写入 Chroma

### 查询流

1. 接收用户问题
2. 检索相关 Chunk
3. 用 Prompt 组织上下文
4. 输出回答、引用来源、建议动作

### 日报流

1. 拉取过去 24 小时资讯
2. 按行业 / 来源聚合
3. 调用 LLM 生成日报
4. 存储 Markdown 报告

## 4. 分层职责

- `api/`：HTTP 层，只做参数接收与结果返回
- `services/`：业务编排层，组织抓取、入库、查询、报告流程
- `crawlers/`：站点抓取与登录逻辑
- `processing/`：文本清洗、表格结构化
- `rag/`：向量库、模型工厂、RAG Prompt
- `storage/`：文件读写与文章仓储
- `mcp/`：MCP 工具暴露层

## 5. 可扩展点

- 站点配置文件化，便于扩展到多行业
- 向量库可替换为 Milvus / Qdrant / pgvector
- 任务调度可接入 Celery / APScheduler
- 日报推送可接入企业微信 / 飞书 / 邮件
