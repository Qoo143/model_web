---
name: rag-skills
description: >
  RAG 系統技能集合。包含 Embedding、VectorStore、Retriever 等主題。
  當用戶詢問 RAG、向量化、檢索、LangChain 相關問題時觸發。
tags: [rag, ai, langchain]
---

# RAG Skills

RAG 系統使用 **LangChain** + **BGE-M3** + **Chroma** 架構。

## 子主題

| Skill | 說明 | 觸發關鍵字 |
|:------|:-----|:-----------|
| [embedder](./embedder/SKILL.md) | Embedding 服務 | embedding, BGE-M3, 向量化 |
| [vectorstore](./vectorstore/SKILL.md) | 向量庫操作 | Chroma, vectorstore |
| [retriever](./retriever/SKILL.md) | 檢索策略 | retriever, 檢索, search |

## RAG 流程

```
使用者提問
    ↓
1. 問題向量化（BGE-M3）
    ↓
2. 向量資料庫檢索（Chroma）
    ↓
3. 取得 Top-K 相關片段
    ↓
4. 構建 Prompt
    ↓
5. LLM 生成答案（Ollama）
    ↓
6. 返回答案 + 來源
```

## 目錄結構

```
backend/app/services/
├── rag/
│   ├── embedder.py       # Embedding 服務
│   ├── vectorstore.py    # Chroma 操作
│   ├── retriever.py      # 檢索策略
│   └── chain.py          # RAG Chain
├── document/
│   ├── parser.py         # 文件解析
│   ├── chunker.py        # 語意分塊
│   └── processor.py      # 處理流程
└── llm/
    ├── base.py           # 抽象基類
    ├── ollama_service.py # Ollama 實作
    └── factory.py        # 工廠模式
```
