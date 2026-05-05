# 智能行业情报分析师

一个面向打工人的行业情报效率工具后端项目，基于 `Python + FastAPI + LangChain + Chroma + MCP` 构建。它不只是“个人知识库”，而是围绕“自动抓取行业资讯、结构化处理、RAG 查询、日报生成、外部工具接入”这一条完整链路来设计。

## 核心能力

- 自动抓取行业资讯、公告、通知页，支持 `requests` 登录或 `Selenium` 模拟登录
- 使用 `Pandas.read_html()` 抽取杂乱 HTML 表格，并落地为 `CSV/JSON`
- 对清洗后的资讯做切分、Embedding、向量检索，构建 RAG 问答能力
- 提供 `FastAPI` RESTful API，支持抓取、入库、查询、日报生成
- 提供 `MCP Server`，便于被桌面 AI 客户端、IDE Agent、工作流系统复用

## 建议场景

- 半导体 / AI / 新能源 / 医药等垂直行业资讯监控
- 竞品动态跟踪、政策公告解读、招投标公告跟踪
- 给业务、产品、战略、销售、运营同学输出行业日报

## 项目结构

```text
.
├─ plan/                      # 规划文档、任务拆解、架构说明
├─ config/
│  └─ sources/                # 站点抓取配置样例
├─ data/
│  ├─ raw/                    # 原始 HTML
│  ├─ processed/              # 清洗后的结构化资讯 JSON
│  ├─ tables/                 # Pandas 导出的 CSV
│  ├─ reports/                # 日报 Markdown / JSON
│  └─ vectorstore/            # Chroma 持久化目录
├─ src/intel_analyst/
│  ├─ api/                    # FastAPI 路由
│  ├─ core/                   # 配置与日志
│  ├─ crawlers/               # requests / Selenium 爬虫
│  ├─ processing/             # HTML 表格结构化
│  ├─ rag/                    # Embeddings / Chroma / Prompt
│  ├─ services/               # 抓取、入库、查询、日报编排
│  ├─ storage/                # 本地文件仓储
│  └─ mcp/                    # MCP Server
└─ tests/                     # 基础单测
```

## 快速启动

1. 创建虚拟环境并安装依赖

```bash
pip install -e .[dev]
```

2. 复制环境变量

```bash
cp .env.example .env
```

3. 启动 FastAPI

```bash
uvicorn intel_analyst.main:app --reload --app-dir src
```

4. 启动 MCP Server

```bash
python -m intel_analyst.mcp.server
```

## 示例接口

- `GET /api/v1/health`
- `POST /api/v1/sources/crawl`
- `POST /api/v1/knowledge/query`
- `POST /api/v1/reports/daily`
- `POST /api/v1/pipeline/rebuild-index`

## 适配真实站点

项目使用配置驱动的抓取方式，先在 `config/sources/` 中定义站点 URL、CSS Selector、登录方式，再通过 API 触发抓取。这样可以把“行业知识库”升级成“多行业情报采集与分析平台”。
