---
name: rag-embedder
description: >
  Embedding 向量化服務規範。當用戶詢問 "embedding"、"BGE-M3"、
  "向量化"、"向量" 時觸發此 Skill。
tags: [rag, embedding, bge-m3]
---

# Embedding 服務規範

## 技術選擇

- **模型**: BGE-M3 (BAAI)
- **維度**: 1024
- **最大長度**: 8192 tokens
- **特點**: 中英文效果優秀

## 服務實作

```python
# backend/app/services/rag/embedder.py
from langchain_community.embeddings import HuggingFaceEmbeddings

class EmbeddingService:
    def __init__(self):
        self.model = HuggingFaceEmbeddings(
            model_name="BAAI/bge-m3",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
    
    def embed_text(self, text: str) -> list[float]:
        """單一文本向量化"""
        return self.model.embed_query(text)
    
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """批次文本向量化"""
        return self.model.embed_documents(texts)
```

## 使用方式

```python
embedder = EmbeddingService()

# 問題向量化
query_vector = embedder.embed_text("營收成長率是多少？")

# 文件向量化
doc_vectors = embedder.embed_documents(chunks)
```

## 效能考量

| 項目 | 建議值 |
|:-----|:-------|
| 批次大小 | 32-64 文本 |
| 最大文本長度 | 512 字元 |
| GPU 加速 | 建議使用 |

## 詳細參考

→ [reference/embedding-guide.md](./reference/embedding-guide.md) - 完整 Embedding 指南
