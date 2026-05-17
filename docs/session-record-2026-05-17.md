# SignalDesk AI 后端接入与调试记录

> 时间：2026-05-17  
> 环境：Windows 11 + Python 3.13 (conda: singnalDesk) + Node.js (Next.js 16)  
> 模型：DeepSeek v4 Flash (API) + BAAI/bge-small-zh-v1.5 (本地嵌入)

---

## 1. 初始状态

项目架构：

```
web/                          ← Next.js 前端 (localhost:3000)
  app/api/
    query/route.ts            → POST /api/query        → 代理到 FastAPI /api/v1/knowledge/query
    crawl/route.ts            → POST /api/crawl        → 代理到 FastAPI /api/v1/sources/crawl
    report/route.ts           → POST /api/report       → 代理到 FastAPI /api/v1/reports/daily
    health/route.ts           → GET  /api/health       → 代理到 FastAPI /api/v1/health

src/intel_analyst/            ← FastAPI 后端 (localhost:8000)
  main.py                     → FastAPI app 入口
  core/config.py              → pydantic-settings 配置
  rag/
    llm.py                    → LLM 工厂 (Ollama / OpenAI 兼容)
    embeddings.py             → 嵌入模型工厂 (HuggingFace / OpenAI)
    vector_store.py           → Chroma 向量库管理
    prompts.py                → RAG / 日报 prompt 模板
  services/
    query_service.py          → RAG 查询服务
    crawler_service.py        → 爬虫服务
    report_service.py         → 日报生成服务
    ingestion_service.py      → 文章入库服务
  api/routes/
    knowledge.py              → /api/v1/knowledge/query
    sources.py                → /api/v1/sources/crawl
    reports.py                → /api/v1/reports/daily
    health.py                 → /api/v1/health
    pipeline.py               → /api/v1/pipeline/rebuild-index
```

前端有 Mock 模式开关，默认开启。Mock 模式下所有请求返回本地硬编码数据，不调用后端。

---

## 2. 环境搭建

### 2.1 安装 Python 依赖

```bash
# 项目在 conda 环境 singnalDesk 中运行
conda run -n singnalDesk pip install hatchling
conda run -n singnalDesk pip install -e f:/workspace3/wen/idea/SignalDesk_AI
```

### 2.2 启动后端

```bash
cd f:/workspace3/wen/idea/SignalDesk_AI
conda run -n singnalDesk uvicorn intel_analyst.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2.3 验证健康检查

```bash
curl http://127.0.0.1:8000/api/v1/health
# → {"status":"ok","environment":"dev","vectorstore_dir":"F:\\...\\data\\vectorstore"}
```

### 2.4 前端 API 代理联通

```bash
curl http://localhost:3000/api/health
# → {"status":"ok","environment":"dev","vectorstore_dir":"F:\\...\\data\\vectorstore"}
```

---

## 3. 问题一：LLM 配置切换（Ollama → DeepSeek）

### 问题

项目默认使用 Ollama（`qwen2.5:7b` 本地模型）。用户机器上没有安装 Ollama，希望改用 DeepSeek API。

### 方案

DeepSeek 提供 OpenAI 兼容 API，所以只需将 `.env` 中的 `llm_provider` 设为 `openai`，并填入 DeepSeek 的 base URL 和 API key。

### 操作

```bash
# .env 文件修改
INTEL_ANALYST_LLM_PROVIDER=openai
INTEL_ANALYST_OPENAI_BASE_URL=https://api.deepseek.com/v1
INTEL_ANALYST_OPENAI_API_KEY=sk-xxxx                 # 用户填入真实 key
INTEL_ANALYST_OPENAI_MODEL=deepseek-v4-flash          # 注意：不是 deepseek-chat
```

用 `/v1/models` 端点验证 key 和可用模型：

```bash
curl https://api.deepseek.com/v1/models \
  -H "Authorization: Bearer sk-xxxx"
# → 返回 deepseek-v4-flash, deepseek-v4-pro
```

### 相关代码

`src/intel_analyst/rag/llm.py`:

```python
def build_chat_model():
    settings = get_settings()
    if settings.llm_provider == "openai":
        return ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return ChatOllama(...)  # fallback
```

---

## 4. 问题二：HuggingFace 连接被墙

### 问题

后端启动后健康检查正常，但首次调用 query / seed 等需要加载嵌入模型（`BAAI/bge-small-zh-v1.5`）的接口时卡死超时。错误日志显示：

```
[WinError 10060] 由于连接方在一段时间后没有正确答复或连接的主机没有反应，连接尝试失败。
```

根因：`huggingface_hub` 下载模型时被 DNS 污染 / 连接重置（国内网络环境）。

### 方案一（失败）：从 hf-mirror 下载缓存

```python
# 通过镜像下载模型到本地缓存
HF_ENDPOINT=https://hf-mirror.com python -c "
from sentence_transformers import SentenceTransformer
SentenceTransformer('BAAI/bge-small-zh-v1.5')
"
```
✅ 下载成功，模型缓存到 `~/.cache/huggingface/hub/`

### 方案二（部分解决）：os.environ.setdefault

在 `embeddings.py` 模块级设环境变量：

```python
import os
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
```

但 uvicorn 子进程可能未正确继承环境变量，`--reload` 模式下的子进程仍然卡死。

### 方案三（最终解决）：在 main.py 入口设环境变量

```python
import os
# Must be set before any HuggingFace imports to use mirror in China
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("HF_HUB_OFFLINE", "1")
```

同时在 `embeddings.py` 也保留一份（双保险）。

### 验证

通过 e2e 测试脚本确认：

```bash
conda run -n singnalDesk python _test_e2e.py
# [1/3] Loading embeddings...   OK (12.4s) — dim=512
# [2/3] Initializing Chroma...  OK (13.9s) — found 0 docs
# [3/3] Testing DeepSeek via LangChain... OK (16.6s)
# ALL PASSED in 16.6s
```

---

## 5. 问题三：向量库为空，Query 返回"无上下文"

### 问题

前端关闭 Mock 模式后调用 `/api/query`，DeepSeek 正确响应但内容为"没有上下文数据"。原因是 Chroma 向量库中没有任何文档。

### 方案：添加 Seed Service 灌入样本数据

不做爬虫（用户暂时聚焦 API/services 模块），而是新增一个 seed 端点，直接向向量库写入 5 篇半导体行业样本文章。

### 新建文件

`src/intel_analyst/services/seed_service.py`：

```python
class SeedService:
    def seed(self) -> int:
        service = IngestionService()
        articles = [self._build_article(data) for data in SAMPLE_ARTICLES]
        return service.ingest_articles(articles)
```

5 篇样本文章覆盖：
1. 深圳半导体产业链协同大会
2. 设备材料企业融资窗口
3. 长三角集成电路产业联盟
4. AI 芯片需求爆发
5. 第三代半导体碳化硅产能

### 注册路由

`src/intel_analyst/api/routes/pipeline.py` 新增：

```python
@router.post("/seed")
def seed_sample_data() -> dict:
    service = SeedService()
    count = service.seed()
    return {"status": "ok", "ingested_count": count}
```

### 执行灌数

```bash
curl -X POST http://127.0.0.1:8000/api/v1/pipeline/seed
# → {"status":"ok","ingested_count":5}
```

---

## 6. 验证完整链路

### Query 测试

```bash
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"question":"半导体行业最近有什么融资动态？","top_k":3}'
```

返回结果（节选）：

```json
{
  "answer": "### 核心结论\n2026年4-5月，国内半导体设备与材料企业进入新一轮融资高峰，已有超过12家企业完成融资，总金额超过80亿元...\n\n### 业务影响\n- 融资活跃意味着行业扩产意愿强...\n\n### 风险提醒\n- 集中融资扩产后若下游需求不及预期...\n\n### 建议动作\n- 优先关注获得本轮融资的设备与材料企业...",
  "citations": [
    {"title": "多家半导体设备与材料企业进入新一轮融资窗口", "url": "https://example.com/news/funding-wave-2026", ...},
    {"title": "深圳半导体产业链协同大会即将召开", "url": "https://example.com/news/sz-semicon-2026", ...}
  ],
  "retrieved_count": 3
}
```

### 前端代理验证

```bash
curl -X POST http://localhost:3000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question":"半导体行业最近有什么融资动态？","top_k":3}'
# → 返回同等内容（通过 Next.js 代理转发到 FastAPI）
```

---

## 7. 最终架构

```
浏览器 (localhost:3000)
  │
  │  关掉 Mock mode
  │
  ▼
Next.js API Route (/api/query)
  │
  │  proxyToBackend("http://127.0.0.1:8000/api/v1/knowledge/query")
  │
  ▼
FastAPI (/api/v1/knowledge/query)
  │
  ├─ VectorStoreManager.similarity_search()  ← Chroma + BAAI/bge-small-zh-v1.5
  │     ↓
  │     返回相关文档片段 (top_k)
  │
  └─ ChatOpenAI(deepseek-v4-flash).invoke()  ← DeepSeek API
        ↓
        基于文档片段生成结构化回答
```

---

## 8. 关键文件变更

| 文件 | 变更类型 | 说明 |
|------|----------|------|
| `.env` | 修改 | LLM 从 Ollama 切到 DeepSeek，模型名修正为 `deepseek-v4-flash` |
| `src/intel_analyst/main.py` | 修改 | 顶部设置 `HF_ENDPOINT` 和 `HF_HUB_OFFLINE` 环境变量 |
| `src/intel_analyst/rag/embeddings.py` | 修改 | 模块级设置 HuggingFace 镜像和离线模式 |
| `src/intel_analyst/services/seed_service.py` | **新增** | Seed 服务，灌入 5 篇半导体行业样本文章 |
| `src/intel_analyst/api/routes/pipeline.py` | 修改 | 新增 `/api/v1/pipeline/seed` 端点 |
| `_test_e2e.py` | **新增** | 嵌入 + 向量库 + LLM 端到端测试脚本 |
| `_download_embeddings.py` | **新增** | 从 hf-mirror 下载嵌入模型 |
| `_test_cache.py` | **新增** | 验证模型能否从本地缓存加载 |

---

## 9. 操作速查

```bash
# 启动后端
cd f:/workspace3/wen/idea/SignalDesk_AI
conda run -n singnalDesk uvicorn intel_analyst.main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端（另一个终端）
cd f:/workspace3/wen/idea/SignalDesk_AI/web
npm run dev

# 灌入样本数据（只需一次）
curl -X POST http://127.0.0.1:8000/api/v1/pipeline/seed

# 测试查询
curl -X POST http://127.0.0.1:8000/api/v1/knowledge/query \
  -H "Content-Type: application/json" \
  -d '{"question":"半导体行业最近有什么融资动态？","top_k":3}'

# 浏览器操作
# 1. 打开 http://localhost:3000
# 2. 点击右侧面板 Mock mode → 关闭（变灰）
# 3. 点击 Refresh 确认后端 Connected
# 4. 输入问题，点 Run Analysis
```
