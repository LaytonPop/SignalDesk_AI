# SignalDesk AI — Smart Industry Intelligence Analyst

## 项目简介

面向打工人的行业情报分析平台。爬取行业新闻 → 向量化入库 → RAG 问答 / 日报生成。
后端 FastAPI + LangChain + Chroma，前端 Next.js。同时提供 MCP 服务给 Claude Desktop 等 AI 助手直接调用。

## 启动命令

```bash
# 后端 (Python 3.11+, conda env: singnalDesk)
cd f:/workspace3/wen/idea/SignalDesk_AI
& "C:/Users/morganWen/.conda/envs/singnalDesk/python.exe" -m uvicorn intel_analyst.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

# 前端
cd web
npm run dev

# MCP Server（可选）
python -m intel_analyst.mcp.server
```

| 服务 | 端口 |
|------|------|
| FastAPI 后端 | 8000 |
| Next.js 前端 | 3000 |
| Ollama（可选） | 11434 |

## 环境配置

- 后端 `.env` — LLM 走 DeepSeek API，Embedding 走本地 `BAAI/bge-small-zh-v1.5`
- 前端 `web/.env.local` — `INTEL_API_BASE_URL=http://127.0.0.1:8000`
- 前端不直接调后端，通过 `web/app/api/*/route.ts` 做反向代理转发

## 技术栈

| 层 | 技术 |
|----|------|
| LLM | DeepSeek (`deepseek-v4-flash`) via OpenAI 兼容协议 |
| Embedding | `BAAI/bge-small-zh-v1.5` (HuggingFace 本地, CPU) |
| 向量库 | Chroma (持久化于 `data/vectorstore/`) |
| 爬虫 | BeautifulSoup + requests + Selenium (认证) |
| 前端 | Next.js 16 (Turbopack) + React 19 |
| MCP | `mcp.server.fastmcp.FastMCP` |

## 架构

```
main.py (FastAPI app)
  └── api/router.py (挂载所有子路由, prefix=/api/v1)
        ├── health.py            GET  /health
        ├── knowledge.py         POST /knowledge/query  → QueryService
        ├── reports.py           POST /reports/daily  → ReportService
        ├── sources.py           POST /sources/crawl  → CrawlerService
        ├── pipeline.py          POST /pipeline/seed  → SeedService
        │                        POST /pipeline/rebuild-index → IngestionService
        └── articles.py          GET  /articles  → ArticleRepository
```

### 核心调用链

```
QueryService.query()
  1. VectorStoreManager.similarity_search() → Chroma 检索
  2. build_rag_prompt() + build_chat_model() → LLM 生成答案
  3. 返回 QueryResponse (answer + citations)

CrawlerService.crawl()
  1. SourceLoader.load() → 解析站点配置 JSON
  2. GenericNewsCrawler.crawl() → 抓取文章列表
  3. IngestionService.ingest_articles() → 切片 → Chroma 入库

ReportService.generate_daily_report()
  1. ArticleRepository.iter_articles() → 读已处理文章
  2. 按时间段筛选 + 拼接上下文
  3. LLM 生成日报 Markdown → FileStore 保存
```

## 数据目录

```
data/
├── raw/         爬虫保存的原始 HTML
├── processed/   清洗后的结构化 JSON（按 source_name 分目录, content_hash.json）
├── tables/      HTML 表格导出的 CSV
├── reports/     日报 Markdown
└── vectorstore/ Chroma 持久化 (chroma.sqlite3)
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/health` | 健康检查 |
| POST | `/api/v1/knowledge/query` | RAG 问答 `{question, top_k}` |
| POST | `/api/v1/reports/daily` | 生成日报 `{report_date, lookback_hours, top_k}` |
| POST | `/api/v1/sources/crawl` | 触发爬虫 `{source_path, source, max_articles}` |
| POST | `/api/v1/pipeline/seed` | 注入 5 篇示例文章到向量库 |
| POST | `/api/v1/pipeline/rebuild-index` | 清空向量库，从 processed/ 全量重建索引 |
| GET | `/api/v1/articles?limit=20` | 文章列表 |

## MCP 工具

| 工具 | 说明 |
|------|------|
| `search_intelligence(question, top_k)` | RAG 问答 |
| `generate_daily_brief(report_date, lookback_hours)` | 生成日报 |
| `crawl_and_ingest(source_path, max_articles)` | 爬取并入库 |
| Resource: `brief://latest` | 获取最新日报内容 |

## 关键注意事项

- **Python 环境**：系统默认 `python` 指向 Anaconda3，必须用 `C:/Users/morganWen/.conda/envs/singnalDesk/python.exe`
- **HF 模型**：`main.py` 顶部设置了 `HF_HUB_OFFLINE=1`，模型必须提前下载到 `~/.cache/huggingface/hub/`。huggingface.co 可直连，不要用 hf-mirror.com
- **DeepSeek API**：只支持 chat/completion，不支持 embedding。embedding 必须走本地 HF 模型
- **爬虫未完成**：当前用 `POST /pipeline/seed` 注入了 5 篇半导体行业模拟文章（数据在 `seed_service.py`），问答可正常测试
- **Service 单例**：`dependencies.py` 所有 getter 加了 `@lru_cache(maxsize=1)`，`build_embeddings()` 也加了，避免每个请求重复加载模型

## 相关文档

| 文档 | 内容 |
|------|------|
| [Roadmap.md](.claude/Roadmap.md) | 新功能规划：混合检索、Agent 化、流式输出、项目重命名 |
| [engineering-maturity-assessment.md](docs/engineering-maturity-assessment.md) | 当前代码缺陷清单（P0/P1/P2），含修复方案和面试应对 |
