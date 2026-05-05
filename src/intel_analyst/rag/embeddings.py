from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from intel_analyst.core.config import get_settings


def build_embeddings():
    settings = get_settings()
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return HuggingFaceEmbeddings(model_name=settings.huggingface_embedding_model)
