---
name: rag-vectorstore
description: >
  Chroma 向量庫操作規範。當用戶詢問 "Chroma"、"vectorstore"、
  "向量資料庫"、"向量庫" 時觸發此 Skill。
tags: [rag, chroma, vectorstore]
---

# 向量庫操作規範

## 技術選擇

- **向量庫**: Chroma
- **模式**: Server 模式 (獨立部署)
- **儲存**: `storage/chroma_server_db/`

## 連接配置

```python
# backend/app/services/rag/vectorstore.py
import chromadb

client = chromadb.HttpClient(
    host="chroma",      # Docker 服務名
    port=8000
)

collection = client.get_or_create_collection(
    name=f"group_{group_id}",
    metadata={"hnsw:space": "cosine"}
)
```

## 基本操作

```python
# 新增文件
collection.add(
    ids=["doc1_chunk1", "doc1_chunk2"],
    embeddings=[vector1, vector2],
    documents=[text1, text2],
    metadatas=[
        {"document_id": 1, "chunk_index": 0},
        {"document_id": 1, "chunk_index": 1}
    ]
)

# 相似度搜尋
results = collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    where={"document_id": {"$in": [1, 2, 3]}}  # 過濾
)

# 刪除
collection.delete(
    where={"document_id": doc_id}
)
```

## 資料結構

每個群組有獨立的 Collection：

| Collection 名稱 | 說明 |
|:----------------|:-----|
| `group_{id}` | 群組專屬知識庫 |

## 詳細參考

→ [reference/chroma-guide.md](./reference/chroma-guide.md) - 完整 Chroma 指南
