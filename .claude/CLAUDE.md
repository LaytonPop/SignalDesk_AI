# SignalDesk AI — Smart Industry Intelligence Analyst

## 项目简介

面向打工人的行业情报分析平台。爬取行业新闻 → 向量化入库 → RAG 问答 / 日报生成。
后端 FastAPI + LangChain + Chroma，前端 Next.js。同时提供 MCP 服务给 Claude Desktop 等 AI 助手直接调用。

## 启动命令

```bash
# 后端 (Python 3.11+, conda env: singnalDesk)
cd f:/workspace3/wen/idea/SignalDesk_AI
"C:/Users/morganWen/.conda/envs/singnalDesk/python.exe" -m uvicorn intel_analyst.main:app --reload --app-dir src --host 127.0.0.1 --port 8000

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
        ├── knowledge.py         POST /knowledge/query      → QueryService
        ├── reports.py           POST /reports/daily        → ReportService
        ├── sources.py           POST /sources/crawl        → CrawlerService
        ├── pipeline.py          POST /pipeline/seed
        │                        POST /pipeline/rebuild-index
        └── articles.py          GET  /articles
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

## 关键注意事项

- **Python 环境**：系统默认 `python` 指向 Anaconda3，必须用 `C:/Users/morganWen/.conda/envs/singnalDesk/python.exe`
- **HF 模型**：`main.py` 顶部设置了 `HF_HUB_OFFLINE=1`，模型必须提前下载到 `~/.cache/huggingface/hub/`。huggingface.co 可直连，不要用 hf-mirror.com
- **DeepSeek API**：只支持 chat/completion，不支持 embedding。embedding 必须走本地 HF 模型
- **爬虫未完成**：当前用 `POST /pipeline/seed` 注入了 5 篇半导体行业模拟文章（数据在 `seed_service.py`），问答可正常测试
- **Service 单例**：`dependencies.py` 所有 getter 加了 `@lru_cache(maxsize=1)`，`build_embeddings()` 也加了，避免每个请求重复加载模型

## 待完善项（按优先级）

### 高优先级

1. **性能 — Service 每次请求重复初始化**（已部分修复）
   - `dependencies.py` 的 getter 已加 `@lru_cache`，`build_embeddings()` 也已缓存
   - 但 `VectorStoreManager` 和 `build_chat_model()` 在每个 Service 内部仍然每次 new 实例时重新初始化

2. **健壮性 — 无全局异常处理中间件**
   - 只有 `sources.py` 做了 try/except，其他路由异常直接 500
   - query 和 report 调外部 API（DeepSeek），网络超时会变成 500 吐给前端

3. **性能 — `pipeline.py` rebuild 无安全防护**
   - 上来就 `reset_collection()` 清空向量库，无误触保护、无确认参数、无 dry-run

### 中优先级

4. **一致性 — `pipeline.py` seed 不走 DI**
   - `rebuild_index` 通过 `Depends(get_ingestion_service)` 注入，但 `seed_sample_data` 直接在函数体内 `SeedService()`

5. **一致性 — `pipeline.py` 返回裸 dict**
   - 返回类型是 `dict[str, int | str]`，其他端点都用 Pydantic `response_model`，OpenAPI schema 会不完整

6. **一致性 — `report_service.py` 方法名与行为不匹配**
   - `file_store.save_json(...)` 保存的是 `.md` 文件，不是 JSON

7. **一致性 — `report_service.py` 使用已废弃的 `datetime.utcnow()`**
   - seed_service.py 用的是 `datetime.now(timezone.utc)`，同一项目两种写法

8. **健壮性 — `articles.py` limit 无上限、无分页**
   - `?limit=10000000` 会打爆内存，没有 offset 无法翻页

9. **健壮性 — `knowledge.py` 空向量库无提示**
   - 检索返回 0 条时，LLM 拿着空 context 可能编造答案，应提前返回提示

### 低优先级

10. **代码设计 — `main.py` `create_app()` 工厂形同虚设**
    - 工厂函数定义了，但模块层立即 `app = create_app()` 实例化，测试无法注入配置

11. **代码设计 — `report_service.py` 日报文件名会互相覆盖**
    - 格式是 `daily_report_{date}.md`，同一天多次请求会覆盖前面的结果

12. **可观测性 — 无请求日志中间件**
    - 无 request ID / correlation ID，无法串联请求链路

13. **可观测性 — LLM 调用无日志**
    - 没有记录 prompt、response、token 用量、延迟，调试 prompt 和控制成本时完全无法追溯

14. **安全性 — 无 rate limiting**
    - query 端点调外部 API 有费用，无限调用有成本风险

## 后续规划

### 混合检索增强

主动引入基于 BM25 的稀疏检索 + 稠密向量的 RRF 融合策略，弥补纯向量检索对关键词匹配的不足。预留 Cross-Encoder 重排序接口，在粗排后对 top-k 做精排，提升检索精度。

### MCP 协议封装

核心情报能力（问答、日报、爬取）已通过 MCP 协议封装，可被 Claude Desktop 等 AI 助手作为"情报中台"直接调用。后续结合大热的开源爬虫工具和浏览器内核增强爬虫能力，覆盖 JS 渲染页面和反爬场景。
