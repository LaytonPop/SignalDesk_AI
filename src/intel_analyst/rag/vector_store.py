"""
向量库管理器 —— 对 Chroma 向量数据库的封装。

职责：
    - 创建/连接 Chroma collection（persist_directory= data/vectorstore/）
    - add_documents(): 文档切片 → embedding → 写入 Chroma，返回切片数量
    - similarity_search(): 用问题向量检索 top_k 篇最相似文档
    - reset_collection(): 删除并重建 collection（用于全量重建索引）

被 IngestionService 和 QueryService 引用，是整个 RAG 管道的存储层。
"""

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from intel_analyst.core.config import get_settings
from intel_analyst.rag.embeddings import build_embeddings


class VectorStoreManager:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.embeddings = build_embeddings()
        self.store = Chroma(
            collection_name=self.settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.settings.vectorstore_dir),
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """将长文档按 chunk_size/chunk_overlap 切成小块，用于提高检索精度。"""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.default_chunk_size,
            chunk_overlap=self.settings.default_chunk_overlap,
        )
        return splitter.split_documents(documents)

    def add_documents(self, documents: list[Document]) -> int:
        """文档列表切片后写入向量库，返回写入的切片总数。"""
        if not documents:
            return 0
        split_docs = self.split_documents(documents)
        self.store.add_documents(split_docs)
        return len(split_docs)

    def similarity_search(self, question: str, top_k: int) -> list[Document]:
        """用问题文本检索 top_k 篇最相似的文档切片。"""
        return self.store.similarity_search(question, k=top_k)

    def reset_collection(self) -> None:
        """删除当前 collection 并重建，保留 embedding 和 persist_directory 配置不变。"""
        try:
            self.store.delete_collection()
        except Exception:
            pass
        self.store = Chroma(
            collection_name=self.settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.settings.vectorstore_dir),
        )
