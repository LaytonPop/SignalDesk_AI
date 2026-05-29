# 工程成熟度评估报告

> 面向简历面试场景：本项目架构设计正确、技术栈选型前沿，但工程细节尚处于 MVP 早期。下面按维度拆解所有已知不足，每条标注严重程度和修复代价。

---

## 评估总览

| 维度 | 当前水平 | 目标水平 | 差距 |
|------|----------|----------|------|
| 架构设计 | ★★★★☆ | ★★★★☆ | 小 |
| 健壮性 | ★★☆☆☆ | ★★★★☆ | **大** |
| 性能优化 | ★★☆☆☆ | ★★★☆☆ | 中 |
| 可观测性 | ★☆☆☆☆ | ★★★☆☆ | **大** |
| 安全性 | ★☆☆☆☆ | ★★★☆☆ | 中 |
| 测试覆盖 | ★★☆☆☆ | ★★★☆☆ | 中 |
| 代码一致性 | ★★★☆☆ | ★★★★☆ | 小 |
| DevOps | ★★☆☆☆ | ★★★☆☆ | 中 |
| 数据管理 | ★★☆☆☆ | ★★★☆☆ | 中 |

---

## 一、架构与设计

### 1.1 工厂函数形同虚设 — `main.py`

**严重程度**：中 | **修复代价**：低

```python
# main.py: 模块层立即实例化
def create_app() -> FastAPI:
    app = FastAPI(...)
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    return app

app = create_app()  # ← 模块导入即执行，测试无法注入配置
```

**问题**：`create_app()` 工厂函数定义了，但 `app = create_app()` 在模块顶层立刻执行。这意味着：
- 测试代码调用 `create_app()` 时，原 `app` 已经存在，uvicorn 直接引用的是模块级实例
- 无法向工厂注入替代配置（如测试数据库路径）
- 模块导入时即触发 `Settings()` 和所有副作用

**面试如何说**：工厂函数为未来的配置注入预留了接口，当前 MVP 阶段用模块级实例简化启动。

**修复方向**：移除模块级 `app = create_app()`，改为 `__main__` 入口或在 `pyproject.toml` 的 `[tool.hatch]` 中指定 `app` 对象。

---

### 1.2 Service 初始化链式重复

**严重程度**：高 | **修复代价**：中

```
每个请求进来：
  QueryService.__init__()
    → VectorStoreManager.__init__() → build_embeddings() (已缓存 ✓)
                                    → Chroma(path)   (每次 new ✗)
    → build_chat_model()            → ChatOpenAI()   (每次 new ✗)
```

**问题**：
- `dependencies.py` 的 `@lru_cache` 只缓存了 Service 实例本身
- 但 `QueryService.__init__()` 中 `VectorStoreManager()` 没有被缓存
- `VectorStoreManager.__init__()` 每调用一次就 new 一个 `Chroma` 客户端
- `build_chat_model()` 也没有被缓存（每次 new `ChatOpenAI`）
- 当前 `@lru_cache(maxsize=1)` 依赖单例，但如果 DI 缓存失效（如热加载），全部重新初始化

**面试如何说**：已识别到这个问题，`build_embeddings()` 已加了缓存，下一步是对 `VectorStoreManager` 和 `build_chat_model()` 做同样处理，彻底消除冷启动延迟。

---

### 1.3 模块加载副作用 — `HF_HUB_OFFLINE` 设置

**严重程度**：低 | **修复代价**：低

```python
# main.py 顶部 — import 即执行
os.environ.setdefault("HF_HUB_OFFLINE", "1")
```

**问题**：任何 `import intel_analyst.main` 都会设置全局环境变量。虽然这里用 `setdefault` 避免了覆盖，但模块导入时的副作用仍不理想。如果测试想用在线模式，必须在这个 import 之前设置好环境变量。

---

## 二、健壮性与错误处理

### 2.1 无全局异常处理中间件

**严重程度**：**严重** | **修复代价**：低

**现状**：FastAPI 没有注册任何 `exception_handler`。只有 `sources.py` 的 `crawl_source()` 做了 try/except（只捕获 `ValueError`）。

**影响面**：

| 端点 | 可能的崩溃场景 | 前端看到什么 |
|------|---------------|-------------|
| `POST /knowledge/query` | DeepSeek API 超时 / 限流 / 返回异常 JSON | **裸 500 Internal Server Error** |
| `POST /reports/daily` | 同上 + 文件写入失败 | **裸 500** |
| `POST /pipeline/rebuild-index` | Chroma 文件锁 / 磁盘满 | **裸 500** |
| `GET /articles` | JSON 文件损坏 | **裸 500** |

**这意味着**：用户在 UI 做一次查询，后端因为 DeepSeek 超时崩了，前端只看到一个红色 500，没有任何有用提示。

**面试如何说**：承认这是当前最优先要修的工程问题。FastAPI 提供了 `@app.exception_handler` 装饰器，可以统一拦截 `RequestValidationError`（参数校验）、`HTTPException`（业务异常）、`Exception`（兜底），返回结构化的错误 JSON。

**修复方向**：

```python
# 应有的结构
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_error", "detail": str(exc), "request_id": request_id},
    )
```

---

### 2.2 外部 API 调用无容错

**严重程度**：**严重** | **修复代价**：中

**现状**：`QueryService.query()` 和 `ReportService.generate_daily_report()` 直接调用 LLM API，没有 retry、没有超时设置、没有降级策略。

```python
# query_service.py — 当前实现
chain = self.prompt | self.llm | self.parser
answer = chain.invoke({"question": payload.question, "context": context})
# ↑ 这里如果 DeepSeek API 挂了，直接抛异常，没有任何重试或降级
```

**缺失的能力**：
- 无请求超时设置（无限等）
- 无重试机制（DeepSeek 偶发 429/503）
- 无 fallback 模型（如 DeepSeek 挂了切 Ollama 本地）
- 无 circuit breaker（连续失败 N 次后短期内不再尝试）

**面试如何说**：项目依赖 `tenacity` 已列入 `pyproject.toml`，但目前未使用。下一步会为 LLM 调用加上指数退避重试 + 超时控制；长期会引入 fallback 模型链。

---

### 2.3 `reset_collection()` 无安全防护

**严重程度**：**严重** | **修复代价**：低

```python
# vector_store.py
def reset_collection(self) -> None:
    try:
        self.store.delete_collection()  # ← 直接删！
    except Exception:
        pass
    self.store = Chroma(...)
```

**问题**：
- 一个无参数的 API 调用直接清空整个向量库
- 无确认参数（`confirm=true`）
- 无 dry-run 模式
- `except Exception: pass` 吞掉所有异常（包括权限错误、文件锁），然后假装成功重建
- 如果删除成功但重建失败 → 向量库处于空状态，没有任何恢复手段

**面试如何说**：Pipeline 端点被设计为管理接口（不是用户面），但确实缺了误触保护。应加入 `confirm` 必填参数 + dry-run 预览 + 删除前快照。

---

### 2.4 空向量库无提示

**严重程度**：中 | **修复代价**：低

```python
# query_service.py — 当前实现
documents = self.vector_store.similarity_search(payload.question, payload.top_k)
context = "\n\n".join(doc.page_content for doc in documents)
# ↑ 如果 documents = []，context = ""，LLM 拿着空上下文回答 → 编造答案
```

**问题**：RAG 的核心价值是"基于来源回答"。如果向量库里没有数据，检索返回 0 条，LLM 在空上下文的 System Prompt 下仍然会编造答案（Prompt 里有"如果上下文不足请说明不知道"，但在实践中 LLM 经常不遵守）。

**修复方向**：检索后检查 `len(documents) == 0`，直接返回"知识库暂无相关数据"而不调 LLM。

---

### 2.5 文章列表无分页、无上限

**严重程度**：中 | **修复代价**：低

```python
# articles.py
@router.get("/articles", response_model=ArticleListResponse)
def list_articles(limit: int = 20) -> ArticleListResponse:
    repository = ArticleRepository()
    items = repository.list_articles(limit=limit)
    # ↑ limit 可以是 10000000，数据全部加载到内存
```

**问题**：
- `limit` 参数无上限校验
- 无 `offset` 分页参数
- `iter_articles()` 一次性加载所有 JSON 文件到内存

---

## 三、性能

### 3.1 FastAPI 路由使用同步函数

**严重程度**：中 | **修复代价**：中

**现状**：所有路由处理函数都是 `def` 而不是 `async def`。

```python
# knowledge.py — 同步路由
@router.post("/query", response_model=QueryResponse)
def query_knowledge(...) -> QueryResponse:  # ← def, 不是 async def
    return query_service.query(payload)
```

**这意味着什么**：
- FastAPI 将同步路由放在线程池中执行（默认 `run_in_threadpool`）
- Chroma 检索和 LLM API 调用都是同步 I/O，会阻塞线程池中的线程
- 并发请求多时，线程池耗尽 → 请求排队

**面试如何说**：对于 MVP 的请求量（个人使用，QPS < 1），同步路由完全够用。生产化方向是用 `asyncio.to_thread` 包装同步调用、或将 Chroma 客户端改为 async 模式、或使用 FastAPI 的 `BackgroundTasks`。

---

### 3.2 全量加载数据到内存

**严重程度**：中 | **修复代价**：中

- `ArticleRepository.iter_articles()`：一次性加载所有 JSON 文件（`return items`，不是 generator）
- `ArticleRepository.list_articles(limit)`：先排序所有文件再切片（`sorted(...)[:limit]`）
- `ReportService.generate_daily_report()`：`iter_articles()` 全量加载后按时间筛选

**100 篇文章**：没问题。
**10000 篇文章**：内存暴涨，启动变慢。

---

## 四、可观测性

### 4.1 无请求日志中间件

**严重程度**：中 | **修复代价**：低

**现状**：无 request ID、无请求耗时记录、无结构化日志上下文。出问题时无法串联 "用户 X 在什么时间做了什么操作，结果如何"。

**应该有**：
- 每个请求自动生成 `X-Request-ID`
- 记录 method、path、status_code、duration_ms
- 结构化日志（JSON 格式，方便接入 ELK/Loki）

---

### 4.2 LLM 调用完全无追踪

**严重程度**：高 | **修复代价**：中

**现状**：每次调 LLM（DeepSeek API）没有任何日志记录。不知道：
- 每次请求消耗了多少 token（prompt_tokens + completion_tokens）
- 花了多少钱
- 响应延迟多少
- Prompt 实际内容是什么（调试时完全抓瞎）

**这意味着**：你无法回答"这个系统一个月 LLM 成本多少"——这对任何调用外部付费 API 的系统都是致命的。

**面试如何说**：LangChain 提供了 callback 机制（`BaseCallbackHandler`），可以在 `on_llm_start` / `on_llm_end` 中记录 token 用量。下一步计划接入。

---

### 4.3 无健康检查深度

**严重程度**：低 | **修复代价**：低

**现状**：`GET /health` 只返回 `status: ok` + `environment` + `vectorstore_dir`。

**应该有**：
- Chroma 连接检查
- Embedding 模型加载状态
- LLM API 连通性
- 磁盘空间

---

## 五、安全

### 5.1 无认证/授权

**严重程度**：中（MVP 可接受） | **修复代价**：中

**现状**：所有 API 端点无任何认证。虽然 `Settings` 中有 `demo_username` / `demo_password` 字段，但代码中完全未使用。

---

### 5.2 无 Rate Limiting

**严重程度**：中 | **修复代价**：低

**现状**：`POST /knowledge/query` 每一次调用都会消耗 DeepSeek API 额度（按 token 计费）。任何人都可以不限频率地调用。一个恶意脚本可以在几分钟内烧掉几十块钱。

**面试如何说**：MVP 阶段运行在本地 localhost，外部不可达。生产化需要加入 slowapi 或 Redis-based rate limiter。

---

### 5.3 MCP Server 无认证

**严重程度**：低（本地运行） | **修复代价**：低

MCP Server（`mcp/server.py`）启动后，任何能连到它端口的 AI 客户端都可以调用 `crawl_and_ingest`、`search_intelligence` 等工具。

---

## 六、测试

### 6.1 测试覆盖极低

**严重程度**：中 | **修复代价**：中

**现状**：`tests/` 目录下有 7 个文件，但只有 `test_health_api.py` 和 `test_article_repository.py` 是标准单元测试。其他都是 `_test_xxx.py` 的探索性脚本。

**缺失的测试**：
- `QueryService.query()` — 核心业务逻辑完全无测试
- `ReportService.generate_daily_report()` — 同上
- `CrawlerService.crawl()` — 同上
- `VectorStoreManager` — 无单元测试
- `IngestionService` — 无单元测试
- API 集成测试（用 TestClient 走完整请求链路）

---

### 6.2 测试依赖真实文件系统

**严重程度**：低 | **修复代价**：中

现有测试直接读写 `data/` 目录，没有使用临时目录或 mock。这意味着：
- 测试会污染开发数据
- 无法并行运行测试
- CI 环境需要完整的目录结构和配置

---

## 七、代码一致性

### 7.1 方法名与行为不匹配

```python
# file_store.py
def save_json(self, directory, filename, content):
    path.write_text(content, encoding="utf-8")
    # ↑ 方法名叫 save_json，实际保存的是纯文本（日报 .md）
```

---

### 7.2 同一项目两种时间处理方式

```python
# seed_service.py — 正确
published_at=datetime(2026, 5, 16, 8, 0, tzinfo=timezone.utc),

# report_service.py — 已废弃
cutoff = datetime.utcnow() - timedelta(...)

# generic_news.py — 已废弃
captured_at=datetime.utcnow(),
```

---

### 7.3 DI 使用不一致

```python
# pipeline.py
@router.post("/rebuild-index")
def rebuild_index(ingestion_service: IngestionService = Depends(get_ingestion_service)):
    # ✓ 走 DI

@router.post("/seed")
def seed_sample_data() -> dict:
    service = SeedService()  # ✗ 直接在函数体内 new
```

---

### 7.4 返回类型不一致

```python
# pipeline.py — 返回裸 dict
def rebuild_index(...) -> dict[str, int | str]:

# knowledge.py — 使用 Pydantic response_model
@router.post("/query", response_model=QueryResponse)
```

裸 dict 不会被 FastAPI 的 OpenAPI schema 生成器完整描述，Swagger UI 中 `pipeline` 的文档会不完整。

---

### 7.5 日报文件名互相覆盖

```python
# report_service.py
filename = f"daily_report_{report_date}.md"
# ↑ 同一天两次请求 → 第二次覆盖第一次
```

应加入时间戳：`daily_report_{report_date}_{timestamp}.md`

---

## 八、DevOps

### 8.1 无 Docker 化

**严重程度**：中 | **修复代价**：中

**现状**：依赖 conda 环境 + 手动启动。换个机器跑需要：
1. 装 Python 3.11+
2. 创建 conda env
3. `pip install -e .[dev]`
4. 下载 HuggingFace 模型（~400MB）
5. 配置 `.env`

**面试场景**：面试官让你演示 → 你花 10 分钟配环境。

**修复方向**：`Dockerfile` + `docker-compose.yml`（后端 + Chroma + 可选的前端），一句 `docker-compose up` 全起来。

---

### 8.2 无 CI/CD

**严重程度**：低（个人项目可接受）

无 GitHub Actions、无自动测试、无 lint 检查。

---

### 8.3 无数据初始化脚本

**严重程度**：低 | **修复代价**：低

**现状**：首次启动后向量库是空的，需要手动调 `POST /pipeline/seed` 注入种子数据才能测试问答。

**修复方向**：在 lifespan 中检测向量库是否为空，若为空自动执行 seed。

---

## 九、数据管理

### 9.1 无增量更新机制

**严重程度**：中 | **修复代价**：中

**现状**：爬虫每次全量抓取，基于 `content_hash` 去重。但没有：
- 增量抓取策略（只抓新文章）
- 向量库增量更新（只入库新 chunk）
- 过期数据清理

---

### 9.2 无数据版本管理

**严重程度**：低

Chroma collection 没有版本概念。`reset_collection()` 是破坏性操作，无法回滚。

---

### 9.3 文件存储无索引

**严重程度**：低

`ArticleRepository` 通过 `glob("*/*.json")` 扫描文件系统。文章量大了以后，每次 `list_articles()` 都要遍历所有文件并按 mtime 排序。

---

## 十、修复优先级路线图

### 面试前必做（投入 2-3 天，ROI 最高）

| 优先级 | 修复项 | 预计耗时 | 面试收益 |
|--------|--------|----------|----------|
| P0 | 找 1 个真实新闻站跑通爬取闭环 | 4h | **极高** — 解决"爬虫没跑过真实站"的致命伤 |
| P0 | 加全局异常处理中间件 | 1h | **高** — 体现工程意识 |
| P0 | 修掉 3 个代码不一致问题（`utcnow`/`save_json`/返回裸 dict） | 30min | **中** — 避免被挑刺 |
| P1 | query 端点加空向量库检查 | 15min | **中** |
| P1 | articles 端点加 limit 上限 | 10min | **低** |

### 面试前建议做（投入 1 天）

| 优先级 | 修复项 | 预计耗时 | 面试收益 |
|--------|--------|----------|----------|
| P1 | Docker Compose 一键启动 | 2h | **极高** — 面试演示可控 |
| P1 | LLM 调用加 retry + timeout（利用已有的 tenacity 依赖） | 1h | **高** |
| P1 | 日报文件名加时间戳 | 10min | **低** |

### 长期优化（入职后再说）

| 优先级 | 修复项 |
|--------|--------|
| P2 | Service 初始化优化（缓存 VectorStoreManager / build_chat_model） |
| P2 | 迭代器改为 generator |
| P2 | LLM 调用日志 + callback |
| P2 | Rate limiting |
| P2 | 认证系统 |
| P2 | CI/CD pipeline |
| P2 | 增量抓取 + 增量入库 |
