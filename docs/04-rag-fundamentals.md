# 04. RAG 基礎原理 - 檢索增強生成

## RAG 是什麼？（生活化比喻）

### 比喻一：開卷考試 vs 閉卷考試

**傳統 LLM（閉卷考試）**：
```
老師：「請說明公司2023年Q3的營收數據」
學生（ChatGPT）：「呃...我不知道,因為我訓練時沒看過貴公司的資料」
```

**RAG 系統（開卷考試）**：
```
老師：「請說明公司2023年Q3的營收數據」
學生（RAG）：
  1. 先翻書（檢索相關文件）
  2. 找到第12頁有相關內容
  3. 根據書上的內容回答：「根據第12頁，Q3營收為5200萬元...」
```

### 比喻二：圖書館員

想像你是圖書館員：

**沒有 RAG 的情況**：
```
讀者：「有關量子力學的書在哪裡？」
你：「不好意思，我記不得所有書的位置...」
```

**有 RAG 的情況**：
```
讀者：「有關量子力學的書在哪裡？」
你的工作流程：
  1. 查詢索引系統（向量資料庫）
  2. 找到相關書籍：
     - 《量子力學導論》在 3F-205
     - 《量子物理學》在 3F-208
  3. 回答：「量子力學的書在三樓205和208書架」
```

**RAG 就是：檢索（Retrieval）+ 增強（Augmented）+ 生成（Generation）**

---

## RAG 的三大核心步驟

```
┌─────────────────────────────────────────────────────┐
│ 步驟 1: Retrieval (檢索)                             │
│ 使用者提問 → 轉成向量 → 在向量資料庫中找相似內容       │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ 步驟 2: Augmented (增強)                             │
│ 將檢索到的內容 + 使用者問題 → 組合成完整 Prompt      │
└─────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────┐
│ 步驟 3: Generation (生成)                            │
│ LLM 根據增強後的 Prompt → 生成有憑有據的答案         │
└─────────────────────────────────────────────────────┘
```

---

## 核心技術一：Embedding (向量化)

### 什麼是 Embedding？

**把文字轉成數字向量，讓電腦能計算「相似度」**

#### 傳統關鍵字搜尋的問題

```
文件內容：「我們公司的營收持續成長」
使用者搜尋：「revenue」

結果：❌ 找不到（因為沒有「revenue」這個詞）
```

#### Embedding 的解決方案

```
文件內容：「我們公司的營收持續成長」
    ↓ 轉換成向量
向量：[0.23, -0.15, 0.87, 0.34, ...]  (1024 維)

使用者搜尋：「revenue」
    ↓ 轉換成向量
向量：[0.25, -0.12, 0.91, 0.32, ...]  (1024 維)

計算相似度：
cos_similarity = 0.89  (很相似！)

結果：✅ 找到了（因為語意相近）
```

### Embedding 如何運作？

想像把「意思」放到多維空間：

```
3D 空間範例（實際是 1024 維）：

           ↑ y軸
           │
    蘋果 ● │  ● 橘子
         │ │ ╱
         │●│╱ 水果
         ├─┼────→ x軸
        ╱  │
       ╱   │
      ╱    │
     ╱     │
  汽車 ●   │
    z軸

相近的概念會在空間中靠近：
- 「蘋果」和「橘子」很近（都是水果）
- 「汽車」離它們很遠（不同類別）
```

### BGE-M3 模型

我們使用的 Embedding 模型：

| 特性 | 說明 |
|------|------|
| 模型名稱 | BAAI/bge-m3 |
| 維度 | 1024 維 |
| 最大長度 | 8192 tokens (~6000 中文字) |
| 語言支援 | 中文、英文、日文等 |
| 用途 | 將文字轉成向量 |

**為什麼選 BGE-M3？**
- 中文效果優秀（BAAI 是中國團隊）
- 支援長文本（8192 tokens）
- 多語言（中英混合也沒問題）
- 開源免費

### 實際操作範例

```python
from sentence_transformers import SentenceTransformer

# 載入模型
model = SentenceTransformer('BAAI/bge-m3')

# 範例文字
texts = [
    "2023年第三季度營收為5200萬元",
    "Q3 revenue is 52 million",
    "公司今年的收入持續成長",
    "我喜歡吃蘋果"
]

# 轉換成向量
embeddings = model.encode(texts)

print(f"向量維度: {embeddings.shape}")
# 輸出: 向量維度: (4, 1024)
# 4 個文字，每個 1024 維

print(f"第一個向量的前10維: {embeddings[0][:10]}")
# 輸出: [0.234, -0.156, 0.789, ...]
```

---

## 核心技術二：向量相似度計算

### Cosine Similarity (餘弦相似度)

最常用的相似度計算方法：

```
公式：
cos(θ) = (A · B) / (||A|| × ||B||)

其中：
- A, B 是兩個向量
- A · B 是內積（點積）
- ||A|| 是向量長度
- θ 是兩向量的夾角

結果：
- 1.0  = 完全相同
- 0.0  = 完全不相關
- -1.0 = 完全相反
```

**視覺化理解**：

```
        ↑ 向量A「營收」
        │╱
        │╱ 夾角小 → 相似度高
        │╱
        └───────→ 向量B「revenue」


        ↑ 向量A「營收」
        │
        │  夾角大 → 相似度低
        │
        └───────────────────→ 向量C「蘋果」
```

### 實際計算範例

```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# 計算所有文字之間的相似度
similarities = cosine_similarity(embeddings)

print("相似度矩陣:")
print(similarities)

# 輸出範例:
#        [0]    [1]    [2]    [3]
# [0]  [1.00   0.89   0.75   0.12]  「2023年Q3營收5200萬」
# [1]  [0.89   1.00   0.72   0.10]  「Q3 revenue is 52M」
# [2]  [0.75   0.72   1.00   0.15]  「公司收入持續成長」
# [3]  [0.12   0.10   0.15   1.00]  「我喜歡吃蘋果」

# 結論:
# - [0] 和 [1] 相似度 0.89（很高！雖然語言不同）
# - [0] 和 [2] 相似度 0.75（也很高）
# - [0] 和 [3] 相似度 0.12（很低，主題不同）
```

---

## 核心技術三：Chroma 向量資料庫

### 什麼是向量資料庫？

**傳統資料庫 (MySQL)**：
- 儲存：結構化資料（表格）
- 查詢：精確匹配
- 範例：`SELECT * WHERE name = '張三'`

**向量資料庫 (Chroma)**：
- 儲存：向量 + 原始文字 + 元資料
- 查詢：相似度搜尋
- 範例：「找出和這個問題最相似的 5 個段落」

### Chroma 的儲存結構

```
Chroma Collection (集合)
│
├─ Document 1
│  ├─ vector: [0.23, -0.15, ...]       # 向量（用來計算相似度）
│  ├─ text: "2023年Q3營收..."          # 原始文字（用來顯示）
│  └─ metadata: {                       # 元資料（用來過濾）
│       "doc_id": 1,
│       "page": 12,
│       "chunk_index": 5,
│       "group_id": 2
│     }
│
├─ Document 2
│  ├─ vector: [0.45, -0.22, ...]
│  ├─ text: "公司收入持續成長..."
│  └─ metadata: {...}
│
└─ Document 3...
```

### Chroma 操作範例

#### 1. 建立 Collection

```python
import chromadb
from chromadb.config import Settings

# 連線到 Chroma (持久化到磁碟)
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./storage/chroma_db"
))

# 建立或取得 Collection
collection = client.get_or_create_collection(
    name="library_documents",
    metadata={"description": "圖書館文件知識庫"}
)
```

#### 2. 新增文件

```python
# 準備資料
texts = [
    "2023年第三季度營收為5200萬元，較去年同期成長18%",
    "公司在Q3推出了三款新產品，市場反應良好",
    "預計2024年將持續投資研發，預算增加25%"
]

# 準備元資料
metadatas = [
    {"doc_id": 1, "page": 12, "chunk_index": 0, "group_id": 2},
    {"doc_id": 1, "page": 15, "chunk_index": 1, "group_id": 2},
    {"doc_id": 1, "page": 20, "chunk_index": 2, "group_id": 2}
]

# 新增到 Chroma (會自動進行 Embedding)
collection.add(
    documents=texts,
    metadatas=metadatas,
    ids=["doc1_chunk0", "doc1_chunk1", "doc1_chunk2"]
)
```

#### 3. 查詢（最重要！）

```python
# 使用者提問
question = "Q3的營收成長了多少？"

# 查詢最相關的 3 個段落
results = collection.query(
    query_texts=[question],
    n_results=3,
    where={"group_id": 2}  # 只在群組2中搜尋
)

print("查詢結果:")
for i, doc in enumerate(results['documents'][0]):
    print(f"\n排名 {i+1}:")
    print(f"內容: {doc}")
    print(f"相似度: {results['distances'][0][i]}")
    print(f"元資料: {results['metadatas'][0][i]}")

# 輸出範例:
# 排名 1:
# 內容: 2023年第三季度營收為5200萬元，較去年同期成長18%
# 相似度: 0.15  (距離越小越相似)
# 元資料: {'doc_id': 1, 'page': 12, 'chunk_index': 0}
#
# 排名 2:
# 內容: 公司在Q3推出了三款新產品，市場反應良好
# 相似度: 0.65
# 元資料: {'doc_id': 1, 'page': 15, 'chunk_index': 1}
```

#### 4. 過濾查詢

```python
# 只在特定文件中搜尋
results = collection.query(
    query_texts=["營收"],
    n_results=5,
    where={
        "$and": [
            {"group_id": 2},           # 群組2
            {"doc_id": {"$in": [1, 3]}}  # 只在文件1和3中搜尋
        ]
    }
)

# 只搜尋特定頁數範圍
results = collection.query(
    query_texts=["研發預算"],
    n_results=5,
    where={
        "$and": [
            {"doc_id": 1},
            {"page": {"$gte": 10, "$lte": 20}}  # 第10-20頁
        ]
    }
)
```

---

## 完整 RAG 流程實作

### 步驟 1: 文件處理和向量化

```python
# 1. 讀取文件
document_text = load_pdf("2023年報.pdf")

# 2. 分塊（Chunking）
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每塊500字
    chunk_overlap=50,      # 重疊50字
    separators=["\n\n", "\n", "。", ".", " "]
)

chunks = splitter.split_text(document_text)
print(f"分成 {len(chunks)} 個塊")
# 輸出: 分成 150 個塊

# 3. 向量化並存入 Chroma
for i, chunk in enumerate(chunks):
    collection.add(
        documents=[chunk],
        metadatas=[{
            "doc_id": 1,
            "chunk_index": i,
            "page": calculate_page(i)  # 根據 chunk 計算頁碼
        }],
        ids=[f"doc1_chunk{i}"]
    )
```

### 步驟 2: 檢索相關段落

```python
def retrieve_relevant_chunks(question: str, top_k: int = 5):
    """檢索最相關的文件片段"""

    # 查詢 Chroma
    results = collection.query(
        query_texts=[question],
        n_results=top_k
    )

    # 整理結果
    chunks = []
    for i in range(len(results['documents'][0])):
        chunks.append({
            "content": results['documents'][0][i],
            "metadata": results['metadatas'][0][i],
            "score": 1 - results['distances'][0][i]  # 轉換為相似度分數
        })

    return chunks

# 測試
question = "2023年Q3營收是多少？"
relevant_chunks = retrieve_relevant_chunks(question, top_k=3)

for chunk in relevant_chunks:
    print(f"相似度: {chunk['score']:.2f}")
    print(f"內容: {chunk['content'][:100]}...")
    print()
```

### 步驟 3: 建構 Prompt

```python
def build_rag_prompt(question: str, chunks: list) -> str:
    """建構 RAG Prompt"""

    # 系統指示
    system_prompt = """你是一個專業的文件分析助手。
請根據提供的參考資料回答問題。

重要規則:
1. 只根據參考資料回答,不要編造資訊
2. 如果資料中找不到答案,明確說「資料中沒有相關資訊」
3. 引用時請標註來源(如:「根據第12頁...」)
4. 使用專業但易懂的語言
"""

    # 參考資料
    context = "\n\n".join([
        f"參考資料 {i+1} (第{chunk['metadata']['page']}頁):\n{chunk['content']}"
        for i, chunk in enumerate(chunks)
    ])

    # 組合完整 Prompt
    full_prompt = f"""{system_prompt}

參考資料:
{context}

使用者問題: {question}

請根據上述參考資料回答:"""

    return full_prompt

# 測試
prompt = build_rag_prompt(question, relevant_chunks)
print(prompt)
```

### 步驟 4: 呼叫 LLM 生成答案

```python
import requests

def generate_answer(prompt: str) -> str:
    """呼叫 Ollama LLM 生成答案"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gpt-oss-20b",
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()
    return result['response']

# 測試完整流程
question = "2023年Q3營收是多少？"

# 1. 檢索
chunks = retrieve_relevant_chunks(question, top_k=3)

# 2. 建構 Prompt
prompt = build_rag_prompt(question, chunks)

# 3. 生成答案
answer = generate_answer(prompt)

print(f"問題: {question}")
print(f"答案: {answer}")
print(f"\n來源:")
for chunk in chunks:
    print(f"  - 第{chunk['metadata']['page']}頁 (相似度: {chunk['score']:.2f})")
```

### 完整範例輸出

```
問題: 2023年Q3營收是多少？

答案: 根據第12頁的資料,2023年第三季度營收為新台幣5,200萬元,較去年同期成長18%。這主要歸功於新產品的推出和市場需求的增加。

來源:
  - 第12頁 (相似度: 0.89)
  - 第15頁 (相似度: 0.72)
  - 第20頁 (相似度: 0.68)
```

---

## RAG vs 其他方法

### 方法一：Fine-tuning (微調)

**優點**：
✅ 模型學習特定領域知識
✅ 不需要外部資料庫

**缺點**：
❌ 成本高（需要大量訓練資料和GPU）
❌ 更新困難（新文件需要重新訓練）
❌ 可能出現幻覺（編造資訊）
❌ 無法追溯來源

### 方法二：直接把文件放進 Prompt

**優點**：
✅ 簡單直接

**缺點**：
❌ Token 限制（LLM 有長度限制）
❌ 成本高（Token 越多越貴）
❌ 效能差（處理大量文字很慢）

範例：
```
Prompt:
【這裡塞入整份100頁的PDF內容...】  ← 會超過限制！

問題: Q3營收是多少？
```

### 方法三：RAG (我們的方法)

**優點**：
✅ 成本低（不需要重新訓練）
✅ 更新容易（新增文件即可）
✅ 可追溯來源（知道答案來自哪裡）
✅ 減少幻覺（基於真實文件回答）
✅ 突破長度限制（只檢索相關部分）

**缺點**：
❌ 需要維護向量資料庫
❌ 檢索品質影響答案品質

---

## RAG 的進階技巧

### 1. Re-ranking (重新排序)

檢索後再用更精確的模型重新排序：

```python
# 第一階段: 快速檢索 (Top-20)
initial_results = collection.query(query_texts=[question], n_results=20)

# 第二階段: 精確重排 (Top-5)
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

scores = reranker.predict([
    (question, doc) for doc in initial_results['documents'][0]
])

# 取分數最高的 5 個
top_5_indices = scores.argsort()[-5:][::-1]
final_results = [initial_results['documents'][0][i] for i in top_5_indices]
```

### 2. Hybrid Search (混合搜尋)

結合關鍵字搜尋和語意搜尋：

```python
# 語意搜尋分數
semantic_score = 0.89

# 關鍵字匹配分數 (BM25)
keyword_score = 0.65

# 混合分數
final_score = 0.7 * semantic_score + 0.3 * keyword_score
```

### 3. Query Expansion (查詢擴展)

用 LLM 產生多個查詢變體：

```python
question = "Q3營收"

# 讓 LLM 生成變體
expanded_queries = llm.generate(f"""
將以下問題改寫成3個不同的表達方式:
{question}
""")

# 結果:
# 1. 第三季度的營收數字是多少？
# 2. 2023年Q3的revenue是多少？
# 3. 三季度銷售收入金額

# 對每個查詢都檢索,然後合併結果
all_results = []
for query in expanded_queries:
    results = collection.query(query_texts=[query], n_results=3)
    all_results.extend(results)

# 去重和重排
final_results = deduplicate_and_rerank(all_results)
```

### 4. Contextual Compression (上下文壓縮)

只保留和問題最相關的句子：

```python
chunk = "第一季度營收3000萬。第二季度營收4000萬。第三季度營收5200萬。第四季度營收6000萬。"
question = "Q3營收"

# 用 LLM 提取相關句子
compressed = llm.generate(f"""
從以下文字中,只提取和問題「{question}」相關的句子:
{chunk}
""")

# 結果: "第三季度營收5200萬。"
# 優點: 減少 Prompt 長度,降低成本
```

---

## 評估 RAG 系統的品質

### 指標 1: Retrieval 品質

**Recall@K (召回率)**：
- 相關文件中有多少被檢索出來
- 公式: `相關且被檢索的數量 / 所有相關文件數量`

```python
# 假設有 10 個相關文件,檢索出 7 個
recall_at_5 = 7 / 10 = 0.7  # 70% 召回率
```

**MRR (Mean Reciprocal Rank)**：
- 第一個相關結果的平均排名

```python
# 第一個相關結果在第2位
MRR = 1/2 = 0.5
```

### 指標 2: Generation 品質

**人工評估**：
- 正確性: 答案是否正確
- 相關性: 答案是否回答問題
- 流暢度: 語言是否自然

**自動評估**：
```python
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy

# 評估答案是否基於參考資料（忠實度）
score = evaluate(
    question=question,
    answer=answer,
    contexts=retrieved_chunks,
    metrics=[faithfulness, answer_relevancy]
)
```

---

## 常見問題

### Q1: Embedding 模型越大越好嗎？

**A**: 不一定
- 更大的模型: 效果可能更好,但速度慢,佔空間
- BGE-M3 (1024維): 平衡點,適合大部分場景
- 可以試試其他模型比較效果

### Q2: Top-K 設多少合適？

**A**: 通常 3-5 個
- 太少: 可能遺漏重要資訊
- 太多: 噪音太多,LLM 容易混淆
- 建議從 5 開始,根據實際效果調整

### Q3: 如何處理多語言文件？

**A**:
- BGE-M3 支援多語言,可以直接用
- 中英混合也沒問題
- 檢索時會自動找語意相近的,不受語言限制

### Q4: Chunk size 怎麼設定？

**A**:
- 太小(< 200字): 上下文不足,語意不完整
- 太大(> 1000字): 包含太多無關資訊
- 建議: 500字,重疊50字
- 根據文件類型調整（技術文件可以小一點,小說可以大一點）

---

## 實戰練習

### 練習 1: 體驗 Embedding

```python
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('BAAI/bge-m3')

# 準備測試文字
texts = [
    "我的貓很可愛",
    "My cat is cute",
    "貓咪非常可愛",
    "今天天氣很好",
    "狗狗很聰明"
]

# 向量化
embeddings = model.encode(texts)

# 計算相似度
sim_matrix = cosine_similarity(embeddings)

# 印出結果
for i, text in enumerate(texts):
    print(f"\n'{text}' 與其他文字的相似度:")
    for j, other_text in enumerate(texts):
        if i != j:
            print(f"  - '{other_text}': {sim_matrix[i][j]:.2f}")
```

### 練習 2: 簡單 RAG 實作

```python
# TODO: 完整的練習程式碼,讓使用者實際跑一遍
```

---

## 下一步

現在你已經理解 RAG 的核心原理,接下來:

1. **學習文件處理**: [05. 文件處理流程](05-document-processing.md)
2. **配置 Ollama**: [06. Ollama 與 LLM 整合](06-ollama-llm.md)
3. **實作完整系統**: [08. 後端實作指南](08-backend-implementation.md)

---

## 延伸閱讀

- [LangChain RAG 教學](https://python.langchain.com/docs/use_cases/question_answering/)
- [Chroma 官方文件](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [論文: Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://arxiv.org/abs/2005.11401)
