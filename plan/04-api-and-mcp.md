# 04. API 与 MCP 设计

## 1. RESTful API

### `GET /api/v1/health`

用途：健康检查与目录初始化状态确认

### `POST /api/v1/sources/crawl`

用途：抓取指定站点资讯并落地到本地数据目录

请求体重点字段：

- `source_path`：站点配置文件路径
- `source`：也可以直接传站点配置对象
- `max_articles`：最多抓取文章数
- `persist_raw`：是否保存原始 HTML
- `auto_ingest`：抓取后是否自动写入向量库

### `GET /api/v1/articles`

用途：查看最近抓到的文章

### `POST /api/v1/knowledge/query`

用途：基于 RAG 进行行业问答

返回内容：

- `answer`
- `citations`
- `retrieved_count`

### `POST /api/v1/reports/daily`

用途：生成日报

返回内容：

- 报告 Markdown
- 引用来源
- 保存路径

### `POST /api/v1/pipeline/rebuild-index`

用途：从已落盘的结构化文章重新构建向量索引

## 2. MCP 设计

### MCP Tools

- `search_intelligence(question, top_k)`
- `generate_daily_brief(report_date, lookback_hours)`
- `crawl_and_ingest(source_path, max_articles)`

### MCP Resources

- `brief://latest`

用途：让外部 Agent 直接拿到最新日报内容

## 3. 为什么要做 MCP

这一步是项目亮点：

- 说明系统不是“封闭式 API”
- 能被 Cursor、Claude Desktop、Agent 工作流等外部系统调用
- 更贴近未来 AI 应用架构

## 4. 返回风格建议

为了体现“打工人效率工具”属性，回答和日报都不只给摘要，而要尽量输出：

- 核心结论
- 业务影响
- 风险提醒
- 下一步建议动作
