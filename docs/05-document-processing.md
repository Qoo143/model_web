# 05. 文件處理流程 - 從上傳到向量化

## 為什麼需要文件處理？

想像你要把一本厚重的百科全書輸入電腦：

```
原始百科全書:
📕 1000頁
📕 包含文字、圖片、表格
📕 不同章節、段落
📕 各種格式（粗體、斜體、標題）

直接問 AI：「這本書講什麼？」
AI: ❌ 「太長了,我無法一次處理1000頁」

經過處理後:
📄 提取純文字
📄 分成 2000 個小段落
📄 每個段落轉成向量
📄 儲存到資料庫

問 AI：「這本書講什麼？」
AI: ✅ 「讓我找找相關段落...根據第 XXX 頁...」
```

**文件處理的目標**：
1. **解析**：從各種格式提取文字
2. **分塊**：切成適合的大小
3. **向量化**：轉成可搜尋的向量
4. **儲存**：放入資料庫供查詢

---

## 完整處理流程

```
┌─────────────────────────────────────────────────┐
│ 步驟 1: 使用者上傳文件                             │
│ example.pdf (5MB)                               │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 2: 檔案驗證                                   │
│ - 檢查格式（PDF/Word/Excel/TXT/MD）               │
│ - 檢查大小（< 50MB）                               │
│ - 檢查權限（使用者是否可上傳到此群組）              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 3: 儲存原始檔案                               │
│ storage/documents/user_1/abc-123-456.pdf        │
│ + 寫入 MySQL (狀態: pending)                     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 4: 解析文件內容                               │
│ PDF → PyMuPDF → 純文字                           │
│ Word → python-docx → 純文字                      │
│ Excel → openpyxl → 純文字                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 5: 語意分塊 (Semantic Chunking)              │
│ 500字一塊, 重疊50字                               │
│ 75頁 → 150 個 chunks                            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 6: 向量化 (Embedding)                        │
│ 使用 BGE-M3 模型                                  │
│ 每個 chunk → 1024 維向量                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 7: 儲存到 Chroma                             │
│ - 向量                                           │
│ - 原始文字                                        │
│ - 元資料 (doc_id, page, chunk_index)            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│ 步驟 8: 更新 MySQL                                │
│ - status: completed                             │
│ - chunk_count: 150                              │
│ - page_count: 75                                │
└─────────────────────────────────────────────────┘
```

---

## 支援的文件格式

### 1. PDF 文件

**使用函式庫**: PyMuPDF (fitz)

**為什麼選 PyMuPDF?**
- 速度快（比 PyPDF2 快 10 倍）
- 支援複雜排版
- 可提取圖片（未來擴展）
- 可保留頁碼資訊

**程式碼實作**:

```python
import fitz  # PyMuPDF

def parse_pdf(file_path: str) -> dict:
    """
    解析 PDF 文件

    Args:
        file_path: PDF 檔案路徑

    Returns:
        {
            "text": "完整文字內容",
            "pages": [
                {"page_num": 1, "text": "第1頁內容"},
                {"page_num": 2, "text": "第2頁內容"},
                ...
            ],
            "metadata": {
                "total_pages": 75,
                "author": "...",
                "title": "..."
            }
        }
    """
    # 開啟 PDF
    doc = fitz.open(file_path)

    pages = []
    full_text = []

    # 逐頁處理
    for page_num in range(len(doc)):
        page = doc[page_num]

        # 提取文字
        text = page.get_text()

        pages.append({
            "page_num": page_num + 1,
            "text": text
        })

        full_text.append(text)

    # 提取元資料
    metadata = {
        "total_pages": len(doc),
        "author": doc.metadata.get("author", ""),
        "title": doc.metadata.get("title", ""),
        "creator": doc.metadata.get("creator", "")
    }

    doc.close()

    return {
        "text": "\n\n".join(full_text),
        "pages": pages,
        "metadata": metadata
    }

# 使用範例
result = parse_pdf("storage/documents/user_1/report.pdf")
print(f"總頁數: {result['metadata']['total_pages']}")
print(f"前100字: {result['text'][:100]}")
```

**處理特殊情況**:

```python
def parse_pdf_advanced(file_path: str) -> dict:
    """進階 PDF 解析（處理掃描件）"""

    doc = fitz.open(file_path)

    # 檢查是否為掃描件（圖片 PDF）
    first_page = doc[0]
    text = first_page.get_text()

    if len(text.strip()) < 50:  # 幾乎沒有文字
        print("警告: 這可能是掃描件，需要 OCR")
        # 未來可以整合 OCR (Tesseract)
        # from pytesseract import image_to_string
        # image = first_page.get_pixmap()
        # text = image_to_string(image)

    return parse_pdf(file_path)
```

---

### 2. Word 文件 (.docx)

**使用函式庫**: python-docx

**程式碼實作**:

```python
from docx import Document

def parse_word(file_path: str) -> dict:
    """
    解析 Word 文件

    Args:
        file_path: Word 檔案路徑

    Returns:
        {
            "text": "完整文字內容",
            "paragraphs": ["段落1", "段落2", ...],
            "metadata": {...}
        }
    """
    doc = Document(file_path)

    paragraphs = []
    full_text = []

    # 提取段落
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:  # 跳過空段落
            paragraphs.append(text)
            full_text.append(text)

    # 提取表格內容
    tables_text = []
    for table in doc.tables:
        table_text = []
        for row in table.rows:
            row_text = [cell.text.strip() for cell in row.cells]
            table_text.append(" | ".join(row_text))
        tables_text.append("\n".join(table_text))

    # 合併表格內容
    if tables_text:
        full_text.extend(tables_text)

    # 提取元資料
    core_properties = doc.core_properties
    metadata = {
        "author": core_properties.author or "",
        "title": core_properties.title or "",
        "created": str(core_properties.created) if core_properties.created else "",
        "modified": str(core_properties.modified) if core_properties.modified else "",
        "paragraph_count": len(paragraphs),
        "table_count": len(doc.tables)
    }

    return {
        "text": "\n\n".join(full_text),
        "paragraphs": paragraphs,
        "metadata": metadata
    }

# 使用範例
result = parse_word("storage/documents/user_1/report.docx")
print(f"段落數: {result['metadata']['paragraph_count']}")
print(f"表格數: {result['metadata']['table_count']}")
```

---

### 3. Excel 文件 (.xlsx)

**使用函式庫**: openpyxl

**程式碼實作**:

```python
from openpyxl import load_workbook

def parse_excel(file_path: str) -> dict:
    """
    解析 Excel 文件

    Args:
        file_path: Excel 檔案路徑

    Returns:
        {
            "text": "完整文字內容",
            "sheets": [
                {"name": "Sheet1", "data": [[...]], "text": "..."},
                ...
            ],
            "metadata": {...}
        }
    """
    wb = load_workbook(file_path, data_only=True)  # data_only=True 讀取公式的結果值

    sheets = []
    full_text = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]

        # 讀取所有資料
        data = []
        sheet_text = []

        for row in ws.iter_rows(values_only=True):
            # 過濾空行
            if any(cell is not None for cell in row):
                data.append(row)
                # 轉成文字（用於向量化）
                row_text = " | ".join([str(cell) if cell is not None else "" for cell in row])
                sheet_text.append(row_text)

        sheets.append({
            "name": sheet_name,
            "data": data,
            "text": "\n".join(sheet_text),
            "row_count": len(data)
        })

        # 加入工作表標題
        full_text.append(f"工作表: {sheet_name}")
        full_text.extend(sheet_text)

    metadata = {
        "sheet_count": len(wb.sheetnames),
        "sheet_names": wb.sheetnames
    }

    wb.close()

    return {
        "text": "\n\n".join(full_text),
        "sheets": sheets,
        "metadata": metadata
    }

# 使用範例
result = parse_excel("storage/documents/user_1/data.xlsx")
print(f"工作表: {result['metadata']['sheet_names']}")
for sheet in result['sheets']:
    print(f"  - {sheet['name']}: {sheet['row_count']} 行")
```

---

### 4. 純文字和 Markdown

**程式碼實作**:

```python
def parse_text(file_path: str, file_type: str = "txt") -> dict:
    """
    解析純文字或 Markdown 文件

    Args:
        file_path: 檔案路徑
        file_type: 'txt' 或 'md'

    Returns:
        {
            "text": "完整文字內容",
            "metadata": {...}
        }
    """
    # 嘗試多種編碼
    encodings = ['utf-8', 'gbk', 'big5', 'latin-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError(f"無法解析檔案編碼: {file_path}")

    # 統計資訊
    lines = text.split('\n')

    metadata = {
        "line_count": len(lines),
        "char_count": len(text),
        "encoding": encoding,
        "file_type": file_type
    }

    return {
        "text": text,
        "metadata": metadata
    }
```

---

## 語意分塊 (Semantic Chunking)

### 為什麼需要分塊？

```
問題: LLM 有長度限制

文件: 100頁 = 50,000 字
LLM 限制: 4,096 tokens ≈ 3,000 字

解決方案: 分塊
- 每塊 500 字
- 100 個塊
- 每次只檢索相關的 5 個塊 → 2,500 字（在限制內）
```

### 分塊策略

#### 策略 1: 固定大小分塊（不推薦）

```python
def chunk_by_size(text: str, size: int = 500) -> list:
    """固定大小分塊"""
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i+size])
    return chunks

# 問題:
text = "這是一個很長的句子，講述了很多重要的內容。但是固定分塊可能會在句子中間切斷，導致..."
chunks = chunk_by_size(text, 50)
# chunks[0] = "這是一個很長的句子，講述了很多重要的內容。但是固定分塊可能會在句子"
# chunks[1] = "中間切斷，導致..."  ← 前半句被切掉了！
```

**問題**:
- 可能切斷句子
- 破壞語意完整性
- 降低檢索準確度

#### 策略 2: 語意分塊（推薦）

**使用 LangChain 的 RecursiveCharacterTextSplitter**:

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def semantic_chunking(text: str) -> list:
    """
    語意分塊

    原理:
    1. 優先按段落分割（\n\n）
    2. 其次按句子分割（。. ）
    3. 最後才按字元分割
    4. 保留重疊區域（維持上下文）
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,           # 目標塊大小
        chunk_overlap=50,         # 重疊區域
        length_function=len,      # 計算長度的函數
        separators=[
            "\n\n",               # 優先級1: 段落
            "\n",                 # 優先級2: 換行
            "。",                 # 優先級3: 句號（中文）
            ".",                  # 優先級4: 句號（英文）
            "！",                 # 優先級5: 驚嘆號
            "？",                 # 優先級6: 問號
            " ",                  # 優先級7: 空格
            ""                    # 優先級8: 字元
        ],
        keep_separator=True       # 保留分隔符
    )

    chunks = splitter.split_text(text)
    return chunks

# 測試
text = """第一章：公司概況

我們公司成立於2010年，主要從事軟體開發業務。經過十多年的發展，已經成為業界領先企業。

第二章：財務狀況

2023年第三季度營收為5,200萬元，較去年同期成長18%。淨利潤達到1,200萬元，毛利率維持在45%。

第三章：未來展望

公司計劃在2024年持續投資研發，預算增加25%。同時將拓展海外市場，預計新增3個辦事處。"""

chunks = semantic_chunking(text)
for i, chunk in enumerate(chunks):
    print(f"\n=== Chunk {i+1} ===")
    print(chunk)
    print(f"長度: {len(chunk)}")
```

**輸出**:
```
=== Chunk 1 ===
第一章：公司概況

我們公司成立於2010年，主要從事軟體開發業務。經過十多年的發展，已經成為業界領先企業。

第二章：財務狀況

2023年第三季度營收為5,200萬元，較去年同期成長18%。
長度: 95

=== Chunk 2 ===
2023年第三季度營收為5,200萬元，較去年同期成長18%。淨利潤達到1,200萬元，毛利率維持在45%。

第三章：未來展望

公司計劃在2024年持續投資研發，預算增加25%。
長度: 105
```

**注意重疊區域**：
- Chunk 1 結尾：「2023年第三季度營收為5,200萬元，較去年同期成長18%。」
- Chunk 2 開頭：「2023年第三季度營收為5,200萬元，較去年同期成長18%。」
- 這樣確保語意連貫！

---

### 保留文件結構資訊

```python
def chunk_with_metadata(parsed_doc: dict, file_type: str) -> list:
    """
    分塊並保留元資料

    Args:
        parsed_doc: 解析後的文件
        file_type: 'pdf', 'docx', 'xlsx', 'txt'

    Returns:
        [
            {
                "text": "chunk 內容",
                "metadata": {
                    "chunk_index": 0,
                    "page": 1,  # 如果是 PDF
                    "source": "..."
                }
            },
            ...
        ]
    """
    chunks_with_meta = []

    if file_type == 'pdf':
        # PDF: 按頁處理，保留頁碼
        for page_info in parsed_doc['pages']:
            page_num = page_info['page_num']
            page_text = page_info['text']

            # 分塊
            chunks = semantic_chunking(page_text)

            for i, chunk in enumerate(chunks):
                chunks_with_meta.append({
                    "text": chunk,
                    "metadata": {
                        "chunk_index": len(chunks_with_meta),
                        "page": page_num,
                        "page_chunk_index": i,  # 該頁的第幾個chunk
                        "source": f"第{page_num}頁"
                    }
                })

    elif file_type == 'docx':
        # Word: 整體分塊
        chunks = semantic_chunking(parsed_doc['text'])

        for i, chunk in enumerate(chunks):
            chunks_with_meta.append({
                "text": chunk,
                "metadata": {
                    "chunk_index": i,
                    "source": f"段落區域 {i+1}"
                }
            })

    elif file_type == 'xlsx':
        # Excel: 按工作表處理
        for sheet in parsed_doc['sheets']:
            sheet_name = sheet['name']
            sheet_text = sheet['text']

            chunks = semantic_chunking(sheet_text)

            for i, chunk in enumerate(chunks):
                chunks_with_meta.append({
                    "text": chunk,
                    "metadata": {
                        "chunk_index": len(chunks_with_meta),
                        "sheet": sheet_name,
                        "source": f"工作表「{sheet_name}」"
                    }
                })

    else:  # txt, md
        chunks = semantic_chunking(parsed_doc['text'])

        for i, chunk in enumerate(chunks):
            chunks_with_meta.append({
                "text": chunk,
                "metadata": {
                    "chunk_index": i,
                    "source": f"區塊 {i+1}"
                }
            })

    return chunks_with_meta
```

---

## 向量化 (Embedding)

### 使用 BGE-M3 模型

```python
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    """Embedding 服務"""

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        """
        初始化

        Args:
            model_name: 模型名稱
        """
        print(f"載入 Embedding 模型: {model_name}")
        self.model = SentenceTransformer(model_name)
        print(f"模型維度: {self.model.get_sentence_embedding_dimension()}")

    def embed_text(self, text: str) -> np.ndarray:
        """
        單個文字向量化

        Args:
            text: 文字內容

        Returns:
            向量 (1024 維)
        """
        return self.model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: list, batch_size: int = 32) -> np.ndarray:
        """
        批次向量化（更快）

        Args:
            texts: 文字列表
            batch_size: 批次大小

        Returns:
            向量陣列 (N x 1024)
        """
        return self.model.encode(
            texts,
            batch_size=batch_size,
            normalize_embeddings=True,
            show_progress_bar=True
        )

# 使用範例
embedder = EmbeddingService()

# 單個文字
text = "2023年Q3營收為5200萬元"
vector = embedder.embed_text(text)
print(f"向量維度: {vector.shape}")  # (1024,)
print(f"向量前5維: {vector[:5]}")

# 批次處理（推薦）
texts = [chunk['text'] for chunk in chunks_with_meta]
vectors = embedder.embed_batch(texts, batch_size=32)
print(f"批次向量化: {vectors.shape}")  # (150, 1024)
```

---

## 儲存到 Chroma

```python
import chromadb
from chromadb.config import Settings

class ChromaService:
    """Chroma 向量資料庫服務"""

    def __init__(self, persist_directory: str = "./storage/chroma_db"):
        """
        初始化

        Args:
            persist_directory: 持久化目錄
        """
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_directory
        ))

    def get_collection(self, name: str):
        """取得或建立 Collection"""
        return self.client.get_or_create_collection(
            name=name,
            metadata={"description": "文件向量庫"}
        )

    def add_document_chunks(
        self,
        collection_name: str,
        chunks: list,
        document_id: int,
        group_id: int
    ):
        """
        新增文件的所有 chunks

        Args:
            collection_name: Collection 名稱
            chunks: chunk 列表（含 metadata）
            document_id: 文件 ID
            group_id: 群組 ID
        """
        collection = self.get_collection(collection_name)

        # 準備資料
        ids = []
        texts = []
        metadatas = []

        for chunk in chunks:
            chunk_id = f"doc{document_id}_chunk{chunk['metadata']['chunk_index']}"

            ids.append(chunk_id)
            texts.append(chunk['text'])

            # 合併元資料
            metadata = {
                **chunk['metadata'],
                "document_id": document_id,
                "group_id": group_id
            }
            metadatas.append(metadata)

        # 批次新增（Chroma 會自動進行 Embedding）
        collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )

        print(f"已新增 {len(chunks)} 個 chunks 到 Chroma")

    def delete_document(self, collection_name: str, document_id: int):
        """刪除文件的所有 chunks"""
        collection = self.get_collection(collection_name)

        # 查詢該文件的所有 chunks
        results = collection.get(
            where={"document_id": document_id}
        )

        if results['ids']:
            collection.delete(ids=results['ids'])
            print(f"已刪除文件 {document_id} 的 {len(results['ids'])} 個 chunks")

# 使用範例
chroma = ChromaService()

# 新增文件
chroma.add_document_chunks(
    collection_name="library_documents",
    chunks=chunks_with_meta,
    document_id=1,
    group_id=2
)
```

---

## 完整處理流程整合

```python
import os
import uuid
from pathlib import Path

class DocumentProcessor:
    """文件處理器"""

    def __init__(
        self,
        storage_dir: str = "./storage/documents",
        chroma_dir: str = "./storage/chroma_db"
    ):
        self.storage_dir = Path(storage_dir)
        self.embedder = EmbeddingService()
        self.chroma = ChromaService(chroma_dir)

    def process_document(
        self,
        file_path: str,
        file_type: str,
        document_id: int,
        group_id: int,
        user_id: int
    ) -> dict:
        """
        處理文件的完整流程

        Args:
            file_path: 檔案路徑
            file_type: 檔案類型 ('pdf', 'docx', 'xlsx', 'txt', 'md')
            document_id: 文件 ID
            group_id: 群組 ID
            user_id: 使用者 ID

        Returns:
            {
                "success": True,
                "chunk_count": 150,
                "page_count": 75,
                "metadata": {...}
            }
        """
        try:
            print(f"開始處理文件: {file_path}")

            # 步驟 1: 解析文件
            print("步驟 1/4: 解析文件...")
            if file_type == 'pdf':
                parsed = parse_pdf(file_path)
                page_count = parsed['metadata']['total_pages']
            elif file_type == 'docx':
                parsed = parse_word(file_path)
                page_count = 0
            elif file_type == 'xlsx':
                parsed = parse_excel(file_path)
                page_count = 0
            else:  # txt, md
                parsed = parse_text(file_path, file_type)
                page_count = 0

            # 步驟 2: 分塊
            print("步驟 2/4: 語意分塊...")
            chunks = chunk_with_metadata(parsed, file_type)
            chunk_count = len(chunks)
            print(f"  分成 {chunk_count} 個 chunks")

            # 步驟 3: 向量化
            print("步驟 3/4: 向量化...")
            # (Chroma 會自動處理，這裡可以預先檢查)

            # 步驟 4: 儲存到 Chroma
            print("步驟 4/4: 儲存到向量資料庫...")
            self.chroma.add_document_chunks(
                collection_name="library_documents",
                chunks=chunks,
                document_id=document_id,
                group_id=group_id
            )

            print("✅ 處理完成！")

            return {
                "success": True,
                "chunk_count": chunk_count,
                "page_count": page_count,
                "metadata": parsed.get('metadata', {})
            }

        except Exception as e:
            print(f"❌ 處理失敗: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

# 使用範例
processor = DocumentProcessor()

result = processor.process_document(
    file_path="storage/documents/user_1/report.pdf",
    file_type="pdf",
    document_id=1,
    group_id=2,
    user_id=1
)

if result['success']:
    print(f"成功處理 {result['chunk_count']} 個 chunks")
else:
    print(f"處理失敗: {result['error']}")
```

---

## 背景任務處理

### 為什麼需要背景任務？

```
同步處理（不推薦）:
使用者上傳文件 → 等待處理（30秒） → 回應

問題：
- 使用者體驗差（要等很久）
- 佔用 API 連線
- 超時風險

背景任務（推薦）:
使用者上傳文件 → 立即回應 → 背景慢慢處理

優點：
- 使用者體驗好
- 不佔用連線
- 可以重試
```

### 使用 Celery 實作背景任務

```python
from celery import Celery

# 初始化 Celery
celery_app = Celery(
    "document_processor",
    broker="redis://localhost:6379/0",  # 訊息佇列
    backend="redis://localhost:6379/0"  # 結果儲存
)

@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: int):
    """
    背景任務: 處理文件

    Args:
        self: Celery task instance
        document_id: 文件 ID
    """
    try:
        # 從資料庫取得文件資訊
        doc = db.query(Document).filter(Document.id == document_id).first()

        # 更新狀態: processing
        doc.processing_status = 'processing'
        db.commit()

        # 處理文件
        processor = DocumentProcessor()
        result = processor.process_document(
            file_path=doc.file_path,
            file_type=doc.file_type,
            document_id=doc.id,
            group_id=doc.group_id,
            user_id=doc.uploaded_by
        )

        if result['success']:
            # 更新狀態: completed
            doc.processing_status = 'completed'
            doc.chunk_count = result['chunk_count']
            doc.page_count = result['page_count']
            db.commit()
        else:
            raise Exception(result['error'])

    except Exception as e:
        # 更新狀態: failed
        doc.processing_status = 'failed'
        doc.error_message = str(e)
        db.commit()

        # 重試（最多3次）
        raise self.retry(exc=e, countdown=60)  # 60秒後重試

# API 端點
@app.post("/api/documents/upload")
async def upload_document(file: UploadFile):
    # 儲存檔案
    file_path = save_file(file)

    # 寫入資料庫
    doc = Document(
        filename=file_path,
        processing_status='pending',
        ...
    )
    db.add(doc)
    db.commit()

    # 啟動背景任務
    process_document_task.delay(doc.id)

    # 立即回應
    return {
        "message": "文件上傳成功，正在處理中",
        "document_id": doc.id,
        "status": "pending"
    }
```

---

## 錯誤處理

### 常見錯誤

#### 1. 檔案損壞

```python
def parse_pdf_safe(file_path: str) -> dict:
    """安全的 PDF 解析"""
    try:
        doc = fitz.open(file_path)

        # 檢查是否能正常開啟
        if len(doc) == 0:
            raise ValueError("PDF 檔案為空")

        # 嘗試讀取第一頁
        first_page = doc[0]
        text = first_page.get_text()

        return parse_pdf(file_path)

    except fitz.fitz.FileDataError:
        raise ValueError("PDF 檔案損壞，無法開啟")
    except Exception as e:
        raise ValueError(f"PDF 解析失敗: {str(e)}")
```

#### 2. 記憶體不足（大檔案）

```python
def parse_large_pdf(file_path: str) -> dict:
    """處理大型 PDF（分批讀取）"""

    doc = fitz.open(file_path)
    total_pages = len(doc)

    # 每次處理 10 頁
    batch_size = 10
    pages = []

    for start in range(0, total_pages, batch_size):
        end = min(start + batch_size, total_pages)

        for page_num in range(start, end):
            page = doc[page_num]
            text = page.get_text()
            pages.append({"page_num": page_num + 1, "text": text})

        # 釋放記憶體
        import gc
        gc.collect()

    doc.close()

    return {"pages": pages, "metadata": {"total_pages": total_pages}}
```

#### 3. 編碼問題

```python
def parse_text_robust(file_path: str) -> dict:
    """強健的文字檔解析"""

    # 嘗試多種編碼
    encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'big5', 'shift-jis', 'latin-1']

    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                text = f.read()

            # 檢查是否有亂碼
            if '�' not in text:  # 替換字元
                return {"text": text, "metadata": {"encoding": encoding}}
        except:
            continue

    # 最後手段: 用二進位模式讀取，忽略錯誤
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    return {"text": text, "metadata": {"encoding": "utf-8 (with errors ignored)"}}
```

---

## 效能優化

### 1. 批次處理

```python
# 不好: 逐個處理
for chunk in chunks:
    vector = embedder.embed_text(chunk['text'])  # 每次都呼叫模型

# 好: 批次處理
texts = [chunk['text'] for chunk in chunks]
vectors = embedder.embed_batch(texts, batch_size=32)  # 一次處理32個
```

### 2. 快取

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def parse_pdf_cached(file_path: str) -> str:
    """快取解析結果（適合重複處理）"""
    return parse_pdf(file_path)['text']
```

### 3. 平行處理（多個文件）

```python
from concurrent.futures import ThreadPoolExecutor

def process_multiple_documents(document_ids: list):
    """平行處理多個文件"""

    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(process_document_task, doc_id)
            for doc_id in document_ids
        ]

        results = [f.result() for f in futures]

    return results
```

---

## 常見問題

### Q1: 為什麼分塊要重疊？

**A**:
```
沒有重疊:
Chunk1: "...公司在2023年"
Chunk2: "第三季度營收為5200萬元..."

問題: 如果問「2023年第三季度營收」,可能兩個都匹配不好

有重疊:
Chunk1: "...公司在2023年第三季度營收為5200萬元..."
Chunk2: "...第三季度營收為5200萬元，較去年..."

優點: 完整的語意，提高檢索準確度
```

### Q2: Chunk size 怎麼決定？

**A**:
- 太小（< 200字）: 語意不完整
- 太大（> 1000字）: 包含太多無關資訊
- 建議：500字，根據文件類型調整
  - 技術文件: 300-400字（資訊密度高）
  - 報告: 500-600字
  - 小說: 800-1000字（需要更多上下文）

### Q3: 如何處理表格？

**A**:
```python
# 方法1: 轉成純文字（簡單但損失結構）
"姓名 | 年齡 | 職位\n張三 | 30 | 工程師"

# 方法2: 用 Markdown 表格（保留結構）
"| 姓名 | 年齡 | 職位 |\n|------|------|------|\n| 張三 | 30 | 工程師 |"

# 方法3: 用 JSON（程式化處理）
{"headers": ["姓名", "年齡", "職位"], "rows": [["張三", 30, "工程師"]]}
```

---

## 下一步

現在你已經了解文件處理的完整流程，接下來:

1. **整合 Ollama**: [06. Ollama 與 LLM 整合](06-ollama-llm.md)
2. **實作完整系統**: [08. 後端實作指南](08-backend-implementation.md)

---

## 延伸閱讀

- [PyMuPDF 文件](https://pymupdf.readthedocs.io/)
- [python-docx 文件](https://python-docx.readthedocs.io/)
- [LangChain Text Splitters](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [Chroma 文件](https://docs.trychroma.com/)
