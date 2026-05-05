# 06. 简历表达与面试亮点

## 1. 简历项目标题建议

`智能行业情报分析师（RAG + MCP）`

副标题可以写：
`Python / FastAPI / LangChain / Chroma / Selenium / Pandas`

## 2. 简历描述建议

- 设计并实现面向知识工作者的行业情报分析后端，支持自动抓取行业新闻、公告和 HTML 表格，并沉淀为可检索知识库
- 使用 `requests / Selenium` 构建可配置爬虫，支持登录态采集与资讯增量落盘
- 使用 `Pandas.read_html()` 将杂乱网页表格转为结构化 `CSV/JSON`，提升数据清洗效率
- 基于 `LangChain + Chroma` 构建 RAG 查询链路，支持带来源引用的行业问答与日报生成
- 基于 `FastAPI` 提供 RESTful API，并通过 `MCP Server` 暴露查询、日报与抓取工具能力

## 3. 面试可重点展开的点

- 为什么要把“个人知识库”升级成“行业情报工作台”
- Selenium 登录和 requests 会话复用怎么配合
- HTML 表格抽取为什么选择 Pandas
- RAG Chunk 粒度、元数据设计、引用追踪怎么做
- 为什么 MCP 是比“只做 API”更前沿的亮点

## 4. 后续可量化指标

- 单次抓取文章数
- 表格结构化成功率
- 日报生成耗时
- 查询命中率 / 人工满意度
- 每天节省的人工整理时间
