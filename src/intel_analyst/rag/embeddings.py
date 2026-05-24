"""
Embedding 模型工厂。

根据配置中 embedding_provider 的值，返回对应的 embedding 模型实例：
    - "huggingface" → 本地 BAAI/bge-small-zh-v1.5 模型（CPU 运行）
    - "openai" → 调用 OpenAI/DeepSeek 兼容的云端 embedding API

被 VectorStoreManager.__init__() 调用，每次向量库操作时都需要 embedding 来向量化文本。
加了 lru_cache 避免重复加载模型到内存。
"""

from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from intel_analyst.core.config import get_settings


@lru_cache(maxsize=1)
def build_embeddings():
    settings = get_settings()
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return HuggingFaceEmbeddings(model_name=settings.huggingface_embedding_model)
