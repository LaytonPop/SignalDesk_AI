# 03. 目录分层规范

## 1. 根目录结构

```text
AI_Talk/
├─ plan/
├─ config/
│  └─ sources/
├─ data/
│  ├─ raw/
│  ├─ processed/
│  ├─ tables/
│  ├─ reports/
│  └─ vectorstore/
├─ src/
│  └─ intel_analyst/
├─ tests/
├─ README.md
├─ pyproject.toml
└─ .env.example
```

## 2. `src/intel_analyst/` 分层

```text
intel_analyst/
├─ api/
│  ├─ dependencies.py
│  ├─ router.py
│  └─ routes/
├─ core/
│  ├─ config.py
│  └─ logging.py
├─ crawlers/
│  ├─ auth.py
│  ├─ base.py
│  ├─ generic_news.py
│  └─ source_loader.py
├─ processing/
│  └─ html_tables.py
├─ rag/
│  ├─ embeddings.py
│  ├─ llm.py
│  ├─ prompts.py
│  └─ vector_store.py
├─ schemas/
│  ├─ article.py
│  ├─ crawl.py
│  ├─ query.py
│  ├─ report.py
│  └─ source.py
├─ services/
│  ├─ crawler_service.py
│  ├─ ingestion_service.py
│  ├─ query_service.py
│  └─ report_service.py
├─ storage/
│  ├─ article_repository.py
│  └─ file_store.py
├─ mcp/
│  └─ server.py
└─ main.py
```

## 3. 分层约束

- `api` 不直接操作爬虫和向量库，统一调用 `services`
- `services` 可以依赖 `crawlers / processing / rag / storage`
- `crawlers` 不依赖 `api`
- `rag` 不关心 HTTP，只关心检索与模型调用
- `storage` 不关心业务语义，只提供文件读写与仓储能力

## 4. 数据目录约定

- `data/raw/`：抓下来的原始 HTML，便于排查 selector 或解析错误
- `data/processed/`：清洗后的文章 JSON
- `data/tables/`：`Pandas` 导出的 CSV 文件
- `data/reports/`：生成的日报 Markdown / JSON
- `data/vectorstore/`：Chroma 持久化存储

## 5. 站点配置目录

`config/sources/` 存放每个站点的配置文件，建议一站一文件，字段包括：

- 基础 URL
- 列表页 URL
- 文章链接 selector
- 标题 / 正文 / 时间 / 标签 selector
- 登录方式和账号环境变量名

这样后续只要“新增配置 + 少量适配代码”就能扩展站点。
