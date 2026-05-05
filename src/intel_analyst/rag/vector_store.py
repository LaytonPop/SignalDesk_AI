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
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.settings.default_chunk_size,
            chunk_overlap=self.settings.default_chunk_overlap,
        )
        return splitter.split_documents(documents)

    def add_documents(self, documents: list[Document]) -> int:
        if not documents:
            return 0
        split_docs = self.split_documents(documents)
        self.store.add_documents(split_docs)
        return len(split_docs)

    def similarity_search(self, question: str, top_k: int) -> list[Document]:
        return self.store.similarity_search(question, k=top_k)

    def reset_collection(self) -> None:
        try:
            self.store.delete_collection()
        except Exception:
            pass
        self.store = Chroma(
            collection_name=self.settings.chroma_collection_name,
            embedding_function=self.embeddings,
            persist_directory=str(self.settings.vectorstore_dir),
        )
