from langchain_core.output_parsers import StrOutputParser

from intel_analyst.rag.llm import build_chat_model
from intel_analyst.rag.prompts import build_rag_prompt
from intel_analyst.rag.vector_store import VectorStoreManager
from intel_analyst.schemas.query import Citation, QueryRequest, QueryResponse


class QueryService:
    def __init__(self) -> None:
        self.vector_store = VectorStoreManager()
        self.llm = build_chat_model()
        self.prompt = build_rag_prompt()
        self.parser = StrOutputParser()

    def query(self, payload: QueryRequest) -> QueryResponse:
        documents = self.vector_store.similarity_search(payload.question, payload.top_k)
        context = "\n\n".join(doc.page_content for doc in documents)
        chain = self.prompt | self.llm | self.parser
        answer = chain.invoke({"question": payload.question, "context": context})
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
