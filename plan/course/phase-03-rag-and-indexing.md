# Phase 3：RAG 与知识层

## 这一阶段你要做出什么

把抓回来的文章变成“可以被问”的知识库，而不是一堆孤立 JSON 文件。

完成后，你应该具备：

- 文本切分
- Embedding 生成
- 向量入库
- 相似检索
- 基于上下文的问答

## 这一阶段涉及的文件

- `src/intel_analyst/rag/embeddings.py`
- `src/intel_analyst/rag/llm.py`
- `src/intel_analyst/rag/vector_store.py`
- `src/intel_analyst/rag/prompts.py`
- `src/intel_analyst/services/ingestion_service.py`
- `src/intel_analyst/services/query_service.py`

## 手把手实现顺序

### Step 1：先想清楚“知识单元”是什么

你要做的事：

- 决定一篇文章如何转成 `Document`
- 把标题、摘要、正文、表格摘要拼成统一文本
- 把 URL、发布时间、来源、行业这些信息放进 metadata

你现在的代码对应位置：

- `src/intel_analyst/services/ingestion_service.py`

重点理解：

- `page_content` 是给模型看的
- `metadata` 是给检索、引用和前端展示用的

### Step 2：建立 Embedding 工厂

你要做的事：

- 默认支持本地开源 Embedding
- 预留 OpenAI-compatible Embedding 切换能力

你现在的代码对应位置：

- `src/intel_analyst/rag/embeddings.py`

验收：

- 不改业务代码，只改环境变量就能切 Embedding 提供方

### Step 3：建立 LLM 工厂

你要做的事：

- 默认支持 `Ollama`
- 预留 `OpenAI-compatible` 接口

你现在的代码对应位置：

- `src/intel_analyst/rag/llm.py`

验收：

- Query Service 不关心底层是哪个模型提供方

### Step 4：接入 Chroma 并做切分

你要做的事：

- 初始化持久化向量库
- 配置 chunk size 和 overlap
- 支持重建索引

你现在的代码对应位置：

- `src/intel_analyst/rag/vector_store.py`

重点理解：

- 为什么资讯类文本不适合切得太碎
- 为什么重建索引能力一定要有

### Step 5：做入库服务

你要做的事：

- 从 `ArticleRecord` 批量转为 `Document`
- 切分后写入向量库
- 提供 `rebuild_index()` 能力

你现在的代码对应位置：

- `src/intel_analyst/services/ingestion_service.py`

验收：

- 结构化文章目录里有内容时，可以重新构建索引

### Step 6：做问答服务

你要做的事：

- 根据问题检索 top-k 文档
- 拼接上下文
- 通过 Prompt 让模型回答
- 返回引用信息

你现在的代码对应位置：

- `src/intel_analyst/rag/prompts.py`
- `src/intel_analyst/services/query_service.py`

重点理解：

- 回答不要只做摘要，要体现“业务影响、风险、动作建议”
- citation 一定要带上标题和 URL，后续前端和面试都很好讲

## 阶段验收清单

- 文章可成功转成向量
- 问题可触发相似检索
- 模型回答能引用资讯来源
- 能重建索引

## 常见坑

- metadata 没设计好，后续 citation 很难补
- chunk 太短，导致上下文碎裂
- 把整篇文章直接塞给模型，不走检索，后续数据一多就崩
