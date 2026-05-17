import os

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

from intel_analyst.core.config import get_settings

# Use hf-mirror when HuggingFace is unreachable (e.g. mainland China)
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
# Prevent hanging on hub access when the model is already cached
os.environ.setdefault("HF_HUB_OFFLINE", "1")


def build_embeddings():
    settings = get_settings()
    if settings.embedding_provider == "openai":
        return OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
    return HuggingFaceEmbeddings(model_name=settings.huggingface_embedding_model)
