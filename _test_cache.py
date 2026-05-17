"""Test: can the model load from cache without HF_ENDPOINT?"""
# Intentionally NOT setting HF_ENDPOINT to test cache-only loading
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-small-zh-v1.5")
emb = model.encode("测试缓存")
print(f"Embedding shape: {emb.shape}")
print("SUCCESS: Loaded from cache!")
