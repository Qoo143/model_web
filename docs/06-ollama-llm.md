# 06. Ollama 與 LLM 整合 - 本地大型語言模型

## Ollama 是什麼？

想像你要請一個「翻譯員」幫你工作：

```
方案 A: 雲端翻譯員（ChatGPT / Gemini）
你: 「請翻譯這份機密文件」
翻譯員: 「好的,請把文件傳給我」
         ↓
      【文件上傳到雲端】← 隱私風險！
         ↓
      「翻譯好了,這是結果」
成本: 每次都要付費

方案 B: 本地翻譯員（Ollama）
你: 「請翻譯這份機密文件」
翻譯員(在你電腦上): 「好的,我在本地處理」
         ↓
      【文件不離開你的電腦】← 隱私安全！
         ↓
      「翻譯好了,這是結果」
成本: 只需要電腦運算資源（免費）
```

**Ollama 是什麼？**
- 讓你在本地運行大型語言模型（LLM）的工具
- 類似 Docker，但專門用於 AI 模型
- 支援多種開源模型（Llama, Mistral, gpt-oss-20b 等）

**為什麼選 Ollama？**
✅ 隱私安全（資料不外傳）
✅ 免費使用（不用付 API 費用）
✅ 離線可用（不需要網路）
✅ Docker 友善（易於部署）
✅ AMD GPU 支援（透過 ROCm）

---

## Ollama vs 其他方案

### 對比表

| 特性 | Ollama | LM Studio | ChatGPT API | Gemini API |
|------|--------|-----------|-------------|------------|
| 部署方式 | 本地 | 本地 | 雲端 | 雲端 |
| 隱私性 | ✅ 高 | ✅ 高 | ❌ 低 | ❌ 低 |
| 成本 | 免費 | 免費 | 付費 | 部分免費 |
| Docker 支援 | ✅ 官方支援 | ❌ 不友善 | N/A | N/A |
| AMD GPU | ✅ 支援 | ❌ 困難 | N/A | N/A |
| API 介面 | OpenAI 相容 | 自訂 | OpenAI | Google |
| 模型管理 | 簡單 | 簡單 | N/A | N/A |
| 效能 | 取決於硬體 | 取決於硬體 | 快 | 快 |

### 適用場景

**選擇 Ollama**:
- 處理敏感資料（醫療、法律、財務）
- 需要離線運行
- 有足夠的硬體資源（8GB+ RAM）
- 需要 Docker 部署

**選擇 ChatGPT/Gemini API**:
- 需要最佳效能
- 沒有隱私顧慮
- 願意付費
- 需要最新模型

---

## 安裝和配置 Ollama

### 方法一: Docker 安裝（推薦）

已經在 `docker-compose.yml` 中配置：

```yaml
ollama:
  image: ollama/ollama:latest
  container_name: library_ollama
  volumes:
    - ./storage/ollama:/root/.ollama  # 模型儲存位置
  ports:
    - "11434:11434"
  devices:  # AMD GPU 支援
    - /dev/kfd:/dev/kfd
    - /dev/dri:/dev/dri
  environment:
    - HSA_OVERRIDE_GFX_VERSION=10.3.0  # AMD GPU 版本
```

**啟動**:
```bash
docker-compose up -d ollama
```

### 方法二: 本地安裝（Windows/macOS/Linux）

**Linux**:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS**:
```bash
brew install ollama
```

**Windows**:
1. 下載：https://ollama.com/download/windows
2. 執行安裝檔

**驗證安裝**:
```bash
ollama --version
# 輸出: ollama version is 0.1.47
```

---

## 下載和管理模型

### 下載模型

```bash
# 進入 Ollama 容器
docker-compose exec ollama bash

# 下載 gpt-oss-20b 模型（約 12GB）
ollama pull gpt-oss-20b

# 下載進度顯示
# pulling manifest
# pulling 8934d96d3f08... 100% ▕████████████████▏ 12 GB
# pulling 8c17c2ebb0ea... 100% ▕████████████████▏ 7.0 KB
# pulling 7c23fb36d801... 100% ▕████████████████▏ 4.8 KB
# pulling 2e0493f67d0c... 100% ▕████████████████▏   59 B
# pulling fa304d675061... 100% ▕████████████████▏   91 B
# pulling 42ba7f8a01dd... 100% ▕████████████████▏  557 B
# verifying sha256 digest
# writing manifest
# removing any unused layers
# success
```

**常用模型**:

| 模型 | 大小 | 參數 | 用途 | 中文支援 |
|------|------|------|------|----------|
| gpt-oss-20b | 12GB | 20B | 通用（推薦） | ✅ 好 |
| llama3:8b | 4.7GB | 8B | 通用（較快） | ⚠️ 中等 |
| llama3:70b | 40GB | 70B | 高品質 | ✅ 好 |
| mistral | 4.1GB | 7B | 快速 | ❌ 差 |
| qwen:14b | 8.2GB | 14B | 中文優化 | ✅ 很好 |

**選擇建議**:
- **學習/測試**: llama3:8b（小巧快速）
- **正式使用**: gpt-oss-20b 或 qwen:14b（平衡點）
- **最佳品質**: llama3:70b（需要強大硬體）

### 管理模型

```bash
# 列出已下載的模型
ollama list

# 輸出:
# NAME            ID              SIZE      MODIFIED
# gpt-oss-20b     abc123...       12 GB     2 minutes ago
# llama3:8b       def456...       4.7 GB    1 day ago

# 刪除模型
ollama rm llama3:8b

# 查看模型資訊
ollama show gpt-oss-20b
```

---

## 測試 Ollama

### 命令列測試

```bash
# 互動式對話
ollama run gpt-oss-20b

>>> 你好，請介紹一下自己
我是一個AI助手，基於大型語言模型...

>>> 2+2等於多少？
2+2等於4。

>>> /bye  # 離開
```

**常用指令**:
- `/bye`: 離開
- `/clear`: 清除對話歷史
- `/show info`: 顯示模型資訊
- `/set parameter temperature 0.7`: 設定參數

### API 測試

```bash
# 使用 curl 測試
curl http://localhost:11434/api/generate -d '{
  "model": "gpt-oss-20b",
  "prompt": "請用一句話介紹 RAG",
  "stream": false
}'

# 回應:
# {
#   "model": "gpt-oss-20b",
#   "created_at": "2024-01-15T10:30:00Z",
#   "response": "RAG是檢索增強生成技術，結合資料檢索和語言生成來提供更準確的答案。",
#   "done": true
# }
```

---

## Python 整合

### 方法一: 使用 Ollama Python 庫

**安裝**:
```bash
pip install ollama
```

**基本使用**:
```python
import ollama

# 簡單生成
response = ollama.chat(
    model='gpt-oss-20b',
    messages=[
        {'role': 'user', 'content': '請問什麼是 RAG?'}
    ]
)

print(response['message']['content'])
# 輸出: RAG（Retrieval-Augmented Generation）是一種結合檢索和生成的技術...
```

**串流輸出**（逐字顯示）:
```python
# 串流模式（像 ChatGPT 一樣逐字出現）
stream = ollama.chat(
    model='gpt-oss-20b',
    messages=[{'role': 'user', 'content': '寫一首詩'}],
    stream=True
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)

# 輸出:
# 春風拂面暖，
# 花開滿枝頭。
# ...
```

### 方法二: 使用 LangChain

**安裝**:
```bash
pip install langchain langchain-community
```

**基本使用**:
```python
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# 初始化 Ollama LLM
llm = Ollama(
    model="gpt-oss-20b",
    base_url="http://localhost:11434",
    temperature=0.7
)

# 簡單呼叫
response = llm.invoke("什麼是向量資料庫？")
print(response)

# 使用 Prompt Template
prompt = PromptTemplate(
    input_variables=["question"],
    template="""你是一個專業的技術助手。請用簡單易懂的方式回答問題。

問題: {question}

回答:"""
)

chain = LLMChain(llm=llm, prompt=prompt)
result = chain.run(question="什麼是 Embedding?")
print(result)
```

---

## RAG 整合

### 完整的 RAG Chain

```python
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# 1. 初始化 Embedding 模型
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3"
)

# 2. 連線到 Chroma 向量資料庫
vectorstore = Chroma(
    collection_name="library_documents",
    embedding_function=embeddings,
    persist_directory="./storage/chroma_db"
)

# 3. 初始化 Ollama LLM
llm = Ollama(
    model="gpt-oss-20b",
    temperature=0.3,  # 降低溫度讓回答更準確
    base_url="http://localhost:11434"
)

# 4. 建立自訂 Prompt
prompt_template = """你是一個專業的文件分析助手。請根據提供的參考資料回答問題。

重要規則:
1. 只根據參考資料回答，不要編造資訊
2. 如果資料中找不到答案，明確說「資料中沒有相關資訊」
3. 引用時請標註來源（如：「根據文件...」）
4. 使用專業但易懂的語言

參考資料:
{context}

使用者問題: {question}

請根據上述參考資料回答:"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# 5. 建立 RAG Chain
rag_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",  # 將所有文件塞進 prompt
    retriever=vectorstore.as_retriever(
        search_kwargs={"k": 5}  # 檢索前 5 個相關文件
    ),
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=True  # 返回來源文件
)

# 6. 使用
result = rag_chain({"query": "2023年Q3營收是多少？"})

print("答案:", result['result'])
print("\n來源:")
for doc in result['source_documents']:
    print(f"  - {doc.metadata.get('source', '未知來源')}")
    print(f"    內容: {doc.page_content[:100]}...")
```

### 進階：自訂 RAG Service

```python
class RAGService:
    """RAG 問答服務"""

    def __init__(
        self,
        llm_model: str = "gpt-oss-20b",
        embedding_model: str = "BAAI/bge-m3",
        chroma_dir: str = "./storage/chroma_db"
    ):
        # 初始化組件
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
        self.vectorstore = Chroma(
            collection_name="library_documents",
            embedding_function=self.embeddings,
            persist_directory=chroma_dir
        )
        self.llm = Ollama(
            model=llm_model,
            temperature=0.3,
            base_url="http://localhost:11434"
        )

    def query(
        self,
        question: str,
        group_id: int = None,
        document_ids: list = None,
        top_k: int = 5
    ) -> dict:
        """
        RAG 問答

        Args:
            question: 使用者問題
            group_id: 群組 ID（過濾用）
            document_ids: 文件 ID 列表（過濾用）
            top_k: 檢索數量

        Returns:
            {
                "answer": "答案內容",
                "sources": [...],
                "metadata": {...}
            }
        """
        # 建立過濾條件
        filter_dict = {}
        if group_id:
            filter_dict["group_id"] = group_id
        if document_ids:
            filter_dict["document_id"] = {"$in": document_ids}

        # 檢索相關文件
        if filter_dict:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={
                    "k": top_k,
                    "filter": filter_dict
                }
            )
        else:
            retriever = self.vectorstore.as_retriever(
                search_kwargs={"k": top_k}
            )

        # 取得相關文件
        docs = retriever.get_relevant_documents(question)

        if not docs:
            return {
                "answer": "抱歉，我在資料中找不到相關資訊。",
                "sources": [],
                "metadata": {"found_docs": 0}
            }

        # 建構 Prompt
        context = "\n\n".join([
            f"參考資料 {i+1}:\n{doc.page_content}"
            for i, doc in enumerate(docs)
        ])

        prompt = f"""你是一個專業的文件分析助手。請根據提供的參考資料回答問題。

重要規則:
1. 只根據參考資料回答，不要編造資訊
2. 如果資料中找不到答案，明確說「資料中沒有相關資訊」
3. 引用時請標註來源
4. 使用專業但易懂的語言

參考資料:
{context}

使用者問題: {question}

請根據上述參考資料回答:"""

        # 生成答案
        answer = self.llm.invoke(prompt)

        # 整理來源
        sources = []
        for doc in docs:
            sources.append({
                "document_id": doc.metadata.get("document_id"),
                "page": doc.metadata.get("page"),
                "content": doc.page_content[:200],  # 前200字
                "source": doc.metadata.get("source", "")
            })

        return {
            "answer": answer,
            "sources": sources,
            "metadata": {
                "found_docs": len(docs),
                "model": "gpt-oss-20b"
            }
        }

# 使用
rag_service = RAGService()

result = rag_service.query(
    question="2023年Q3營收是多少？",
    group_id=2,
    top_k=5
)

print(result['answer'])
```

---

## Prompt Engineering（提示詞工程）

### 什麼是 Prompt Engineering？

**Prompt** = 給 LLM 的指示

```
差的 Prompt:
「Q3營收」

問題:
- 太簡短
- 沒有上下文
- LLM 不知道怎麼回答

好的 Prompt:
「你是專業的財務分析師。請根據以下財報資料，回答2023年第三季度的營收數字，並說明與去年同期的比較。

資料: [...]

請用以下格式回答:
- Q3營收: XXX萬元
- 年增率: XX%
- 說明: ...」

優點:
- 角色定位清楚
- 任務明確
- 有輸出格式
```

### RAG Prompt 模板

```python
system_prompt = """你是一個專業的文件分析助手，專門幫助使用者從文件中找到需要的資訊。

你的職責:
1. 仔細閱讀參考資料
2. 根據資料回答問題
3. 引用具體的來源
4. 使用清晰易懂的語言

你的限制:
1. 絕對不編造資訊
2. 如果資料中沒有答案，誠實說「找不到相關資訊」
3. 不做超出資料範圍的推測"""

user_prompt_template = """參考資料:
{context}

使用者問題: {question}

請根據參考資料回答，並註明來源:"""
```

### 參數調整

```python
llm = Ollama(
    model="gpt-oss-20b",

    # Temperature: 控制創造性
    # 0.0 = 確定性高（適合 RAG）
    # 1.0 = 創造性高（適合創作）
    temperature=0.3,

    # Top P: 控制詞彙多樣性
    # 0.9 = 較多樣（推薦）
    top_p=0.9,

    # Top K: 限制候選詞數量
    top_k=40,

    # Num Predict: 最大生成長度
    num_predict=512,

    # Stop sequences: 停止生成的標記
    stop=["使用者:", "User:"]
)
```

**調整建議**:

| 場景 | Temperature | Top P | Top K |
|------|-------------|-------|-------|
| RAG 問答 | 0.2 - 0.4 | 0.9 | 40 |
| 摘要生成 | 0.3 - 0.5 | 0.9 | 50 |
| 創意寫作 | 0.7 - 0.9 | 0.95 | 100 |
| 程式生成 | 0.1 - 0.3 | 0.95 | 50 |

---

## 效能優化

### 1. AMD GPU 加速

**檢查 GPU 是否被使用**:
```bash
# 在 Ollama 容器中
docker-compose exec ollama bash

# 檢查 ROCm
rocm-smi

# 測試模型
ollama run gpt-oss-20b "測試" --verbose
# 應該顯示: GPU layers: 33/33
```

**沒有使用 GPU 的症狀**:
- 生成速度很慢（> 5秒/回答）
- `rocm-smi` 顯示 GPU 使用率 0%

**解決方法**:
```yaml
# docker-compose.yml
ollama:
  devices:
    - /dev/kfd:/dev/kfd
    - /dev/dri:/dev/dri
  environment:
    - HSA_OVERRIDE_GFX_VERSION=10.3.0  # 確認版本正確
    - OLLAMA_DEBUG=1  # 開啟除錯
```

### 2. 模型量化

**什麼是量化？**
- 將模型從 FP16 壓縮到 Q4_K_M（4-bit）
- 大小減少 75%
- 速度提升 2-4 倍
- 品質略降（通常可接受）

```bash
# 下載量化版本
ollama pull gpt-oss-20b:q4_K_M  # 4-bit 量化

# 比較
# gpt-oss-20b          12GB   原始版本
# gpt-oss-20b:q4_K_M   3GB    量化版本
```

### 3. 批次處理

```python
# 不好: 逐個處理
for question in questions:
    answer = llm.invoke(question)

# 好: 批次處理
answers = llm.batch(questions)
```

### 4. 快取

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_query(question: str) -> str:
    """快取查詢結果"""
    return llm.invoke(question)

# 相同問題會直接返回快取結果
answer1 = cached_query("什麼是 RAG?")  # 呼叫 LLM
answer2 = cached_query("什麼是 RAG?")  # 直接返回快取（快！）
```

---

## 常見問題

### Q1: 為什麼回答很慢？

**可能原因**:
1. 沒有使用 GPU
2. 模型太大（70B 以上）
3. RAM/VRAM 不足

**解決方法**:
```bash
# 檢查 GPU 使用
rocm-smi

# 換小一點的模型
ollama pull llama3:8b

# 使用量化版本
ollama pull gpt-oss-20b:q4_K_M
```

### Q2: 為什麼回答不準確？

**可能原因**:
1. Temperature 太高
2. 檢索到的文件不相關
3. Prompt 不夠明確

**解決方法**:
```python
# 降低 temperature
llm = Ollama(model="gpt-oss-20b", temperature=0.2)

# 增加檢索數量
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# 優化 Prompt
prompt = "你是專業助手。請根據資料回答，不要編造。\n\n資料: {context}\n\n問題: {question}"
```

### Q3: 如何切換到 Gemini API？

**低耦合設計**:
```python
from abc import ABC, abstractmethod

class BaseLLMService(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class OllamaService(BaseLLMService):
    def generate(self, prompt: str) -> str:
        llm = Ollama(model="gpt-oss-20b")
        return llm.invoke(prompt)

class GeminiService(BaseLLMService):
    def generate(self, prompt: str) -> str:
        import google.generativeai as genai
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text

# 使用
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # 從環境變數選擇

if LLM_PROVIDER == "ollama":
    llm_service = OllamaService()
elif LLM_PROVIDER == "gemini":
    llm_service = GeminiService()

answer = llm_service.generate("什麼是 RAG?")
```

---

## 下一步

現在你已經掌握 Ollama 和 LLM 整合，接下來:

1. **學習認證系統**: [07. 認證與權限系統](07-auth-permission.md)
2. **實作完整後端**: [08. 後端實作指南](08-backend-implementation.md)

---

## 延伸閱讀

- [Ollama 官方文件](https://ollama.com/)
- [LangChain Ollama 整合](https://python.langchain.com/docs/integrations/llms/ollama)
- [Prompt Engineering 指南](https://www.promptingguide.ai/)
- [ROCm 官方文件](https://rocm.docs.amd.com/)
