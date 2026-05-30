# IntelFlow — 项目升级路线图

> 将 SignalDesk_AI（课程级 RAG 演示）升级为 IntelFlow（准生产级智能情报中台）。
> 本文档聚焦**新功能规划**。当前代码缺陷和修复清单见 [engineering-maturity-assessment.md](../docs/engineering-maturity-assessment.md)。

---

## 总览

| # | 目标 | 阶段 |
|---|------|------|
| 1 | 混合检索 — BM25 + 稠密向量 + RRF 融合 | 第 2 阶段 |
| 2 | Agent 化 — LangGraph + MCP 工具编排 | 第 3 阶段 |
| 3 | 流式输出 — SSE + 前端逐 token 渲染 | 第 4 阶段 |
| 4 | 项目重命名 — SignalDesk_AI → IntelFlow | 第 5 阶段 |

> 基础加固（爬虫容错、可观测性、Docker 化）属于代码缺陷修复，详见 engineering 文档的第 二/四/八 章。

---

## 1. 混合检索增强

**问题**：纯稠密向量在精确数字、产品型号、罕见术语查询下召回率低。例如 "2024 Q3 营收增长超 20% 的公司" —— 向量模型容易忽略 "20%" 这个约束。

**方案**：BM25 稀疏检索 + 稠密向量 + RRF 融合 + Cross-Encoder 重排序（预留）

| 组件 | 选型 | 解决的问题 |
|------|------|-----------|
| 稀疏检索 | BM25（`rank_bm25`） | 精确匹配关键词、数字、短语 |
| 稠密检索 | 现有 Chroma + `BAAI/bge-small-zh-v1.5` | 语义相似、同义词泛化 |
| 融合策略 | RRF（Reciprocal Rank Fusion） | 无监督融合，免调权重 |
| 重排序 | Cross-Encoder（`bge-reranker-base`，预留） | 精排 top-k，提高首位准确率 |

**实施**：

1. 新增 `src/intel_analyst/rag/hybrid_retriever.py`
2. 实现 RRF：`score = Σ 1/(k + rank_i)`
3. 配置中加 `use_reranker: false` 开关
4. `benchmark.py` 输出 Recall@5 / MRR 对比表

**预期**：Recall@5 提升 15~25%，MRR 提升 20%+。

---

## 2. Agent 化 — 从被动问答到自主决策

**问题**：当前是 "用户问 → 检索一次 → 生成一次"。真正的 Agent 应能：规划步骤 → 调用多个工具 → 根据中间结果决策。

**目标场景**：

> 用户："对比今天 A 公司和 B 公司的新闻，如果其中一家股价下跌，帮我查原因。"
>
> Agent：① 分别检索 A 和 B 的新闻 → ② 发现股价信息不在库中，调用 `web_search` → ③ 综合推理输出分析。

**方案**：LangGraph 构建 ReAct Agent + MCP 工具集

| MCP 工具 | Agent 可编排的复杂任务 |
|----------|----------------------|
| `search_intelligence(query, top_k)` | 多轮检索 + 交叉验证 |
| `generate_daily_brief(date)` | 对比不同日期的情绪变化 |
| `crawl_and_ingest(source, max)` | Agent 自主判断何时需要新数据 |
| （新增）`web_search(query)` | 知识库无答案时自动联网 |

**实施**：

1. MCP 工具粒度拆分（每个函数独立 `@mcp.tool()`）
2. 新增 `src/intel_analyst/agent/` 模块，用 LangGraph 串联工具调用
3. 编写 `docs/MCP_INTEGRATION.md`，教用户配置 Claude Desktop
4. 录制 60 秒演示：一句话触发多步 Agent 推理

**面试价值**：设计可被推理编排的能力原子，比单纯做 RAG 高一个层级。

---

## 3. 流式输出

**问题**：LLM 生成需 5~15 秒，用户盯着空白页面等待。

**方案**：SSE 流式输出

| 端 | 实现 |
|----|------|
| 后端 | FastAPI `StreamingResponse` + `async for chunk in llm.astream()` |
| 前端 | `fetch` + `ReadableStream` 逐 token 渲染 |
| 进阶 | React Suspense + Next.js streaming SSR |

**实施**：

1. 新增 `/api/v1/chat/stream` 端点，返回 `text/event-stream`
2. 前端 `IntelligenceWorkbench` 增加流式渲染
3. 编写 `docs/STREAMING.md`

---

## 4. 项目重命名

**问题**："SignalDesk" 在 GitHub 和商业领域已被多款产品占用。

**方案**：重命名为 **IntelFlow**（Intelligence + Flow）

- 简短、无商业冲突、可派生子模块（`intelflow-core`、`intelflow-mcp`）

**行动**：改仓库名 → 全局替换代码中的 `SignalDesk_AI` → README 加更名说明。

---

## 实施路线图（~10 天）

```
基础加固（engineering doc）     混合检索             Agent 化
┌─────────────────────┐      ┌──────────────┐      ┌──────────────┐
│ □ 爬虫重试+失败队列  │      │ □ BM25 集成   │      │ □ MCP 工具拆分│
│ □ loguru 结构化日志  │  →   │ □ RRF 融合    │  →   │ □ LangGraph   │
│ □ /metrics 端点     │      │ □ benchmark  │      │ □ MCP 集成文档│
│ □ docker-compose    │      └──────────────┘      └──────────────┘
└─────────────────────┘           2 天                    2 天
       2 天

流式输出                        作品集收尾
┌──────────────┐              ┌─────────────────────┐
│ □ SSE 端点    │              │ □ 回归测试用例       │
│ □ 前端流式    │          →   │ □ 架构图 + 演示视频  │
│ □ 部署 Demo   │              │ □ 重命名为 IntelFlow │
└──────────────┘              └─────────────────────┘
      2 天                            2 天
```

## 升级后效果

| 维度 | 当前 | 目标 |
|------|------|------|
| 检索精度 | 纯稠密向量 | BM25 + 向量 + RRF 混合 |
| 架构层级 | RAG 被动问答 | ReAct Agent + MCP 工具集 |
| 用户体验 | 同步阻塞 5~15s | SSE 流式逐 token 输出 |
| 项目命名 | SignalDesk（已被占用） | IntelFlow |
