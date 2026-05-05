# 阶段提交与验收总表

这份表适合你边做边打勾，也适合后面整理 git commit 或项目周报。

## Phase 1：项目基础层

建议提交节点：

- `chore: initialize project structure and FastAPI app`

完成标志：

- 能启动 FastAPI
- `GET /api/v1/health` 可访问
- `.env` 配置可读取
- 数据目录会自动创建

核心文件：

- `src/intel_analyst/main.py`
- `src/intel_analyst/core/config.py`
- `src/intel_analyst/core/logging.py`
- `src/intel_analyst/api/routes/health.py`

## Phase 2：采集与结构化层

建议提交节点：

- `feat: add configurable crawler and html table extraction`

完成标志：

- 能加载站点配置
- 能抓取文章详情页
- 能生成结构化文章 JSON
- 能导出 CSV 表格

核心文件：

- `src/intel_analyst/crawlers/auth.py`
- `src/intel_analyst/crawlers/generic_news.py`
- `src/intel_analyst/processing/html_tables.py`
- `src/intel_analyst/storage/article_repository.py`

## Phase 3：RAG 与知识层

建议提交节点：

- `feat: build rag ingestion and query pipeline`

完成标志：

- 文章能完成向量化入库
- 支持相似检索
- 支持带 citation 的问答

核心文件：

- `src/intel_analyst/rag/vector_store.py`
- `src/intel_analyst/services/ingestion_service.py`
- `src/intel_analyst/services/query_service.py`

## Phase 4：接口与协作层

建议提交节点：

- `feat: expose crawling and rag capabilities via api and mcp`

完成标志：

- 抓取 API 可用
- 查询 API 可用
- MCP server 可启动
- MCP tools 可返回结果

核心文件：

- `src/intel_analyst/api/routes/`
- `src/intel_analyst/mcp/server.py`

## Phase 5：日报与工程增强层

建议提交节点：

- `feat: add daily report generation and baseline tests`

完成标志：

- 日报可生成
- 基础测试可运行
- README 启动说明完整

核心文件：

- `src/intel_analyst/services/report_service.py`
- `tests/`
- `README.md`

## 建议你每阶段都记录的内容

- 这一阶段我解决了什么问题
- 我改了哪些文件
- 我怎么验证它是对的
- 我遇到了什么坑
- 如果面试官追问，我会怎么讲
