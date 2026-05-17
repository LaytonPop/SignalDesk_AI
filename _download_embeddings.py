"""Download embedding model from HuggingFace mirror (modelscope or hf-mirror)."""
import os
import sys

# Try hf-mirror first
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

from sentence_transformers import SentenceTransformer

model_name = "BAAI/bge-small-zh-v1.5"
print(f"Downloading {model_name} from hf-mirror...")
model = SentenceTransformer(model_name)
print("Download complete!")

emb = model.encode("测试嵌入")
print(f"Embedding shape: {emb.shape}")
print("SUCCESS: Embedding model works!")
