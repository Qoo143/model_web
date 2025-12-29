---
name: rag-retriever
description: >
  檢索策略規範。當用戶詢問 "retriever"、"檢索"、
  "search"、"Top-K" 時觸發此 Skill。
tags: [rag, retriever, search]
---

# 檢索策略規範

## 檢索流程

```
1. 用戶選擇文件範圍（可選）
2. 問題向量化
3. 相似度搜尋 (Cosine Similarity)
4. 取 Top-K 結果
5. 分數過濾
6. 返回相關片段
```

## 基本實作

```python
# backend/app/services/rag/retriever.py

class Retriever:
    def __init__(self, vectorstore, embedder):
        self.vectorstore = vectorstore
        self.embedder = embedder
    
    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        document_ids: list[int] | None = None,
        min_score: float = 0.5
    ) -> list[RetrievalResult]:
        # 1. 問題向量化
        query_vector = self.embedder.embed_text(query)
        
        # 2. 向量搜尋
        results = self.vectorstore.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where={"document_id": {"$in": document_ids}} if document_ids else None
        )
        
        # 3. 分數過濾
        filtered = [
            r for r in results
            if r['score'] >= min_score
        ]
        
        return filtered
```

## 參數調整

| 參數 | 預設值 | 說明 |
|:-----|:-------|:-----|
| `top_k` | 5 | 返回結果數量 |
| `min_score` | 0.5 | 最低相似度 |
| `chunk_size` | 500 | 分塊大小 |
| `chunk_overlap` | 50 | 重疊區域 |

## 文件選擇機制

用戶可在前端勾選要檢索的文件，只在選中的文件中搜尋：

```python
# 前端傳來
selected_docs = [1, 3, 5]

# 後端過濾
retriever.retrieve(
    query=question,
    document_ids=selected_docs
)
```
