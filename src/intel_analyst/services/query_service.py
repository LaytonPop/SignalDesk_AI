"""
RAG 问答服务 —— 整个项目的核心业务逻辑。

流程：
    1. 用户提问 → 向量库相似度检索 top_k 篇文档
    2. 拼接文档内容为上下文
    3. 将 {question, context} 填入 prompt → LLM 生成回答
    4. 返回答案 + 引用列表 + 检索数量

被 POST /api/v1/knowledge/query 调用（唯一入口）。
也被 mcp/server.py 的 search_intelligence tool 调用。
"""

from langchain_core.output_parsers import StrOutputParser

from intel_analyst.rag.llm import build_chat_model
from intel_analyst.rag.prompts import build_rag_prompt
from intel_analyst.rag.vector_store import VectorStoreManager
from intel_analyst.schemas.query import Citation, QueryRequest, QueryResponse


class QueryService:
    def __init__(self) -> None:
        self.vector_store = VectorStoreManager()  # Chroma + embedding 模型
        self.llm = build_chat_model()             # DeepSeek/Ollama LLM
        self.prompt = build_rag_prompt()          # RAG 的 system/user prompt 模板
        self.parser = StrOutputParser()           # 把 LLM 输出转为纯文本

    def query(self, payload: QueryRequest) -> QueryResponse:
        # Step 1: 向量检索
        documents = self.vector_store.similarity_search(payload.question, payload.top_k)
        context = "\n\n".join(doc.page_content for doc in documents)

        # Step 2: LLM 生成
        chain = self.prompt | self.llm | self.parser
        answer = chain.invoke({"question": payload.question, "context": context})

        # Step 3: 构造引用列表
        citations = [
            Citation(
                title=doc.metadata.get("title", "Untitled"),
                url=doc.metadata.get("url", ""),
                published_at=doc.metadata.get("published_at") or None,
                snippet=doc.page_content[:240],
            )
            for doc in documents
        ]
        return QueryResponse(
            answer=answer,
            citations=citations,
            retrieved_count=len(documents),
        )
