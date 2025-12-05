"""
RAG Chain

整合檢索和生成的完整 RAG 流程
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

from app.services.rag.retriever import RetrieverService, retriever_service, RetrievalResult
from app.services.llm.base import BaseLLMService, Message
from app.services.llm.factory import get_llm_service
from app.core.config import settings


@dataclass
class RAGResponse:
    """RAG 回應"""
    answer: str
    sources: List[Dict[str, Any]]
    model: str
    retrieval_count: int
    generation_time: Optional[float] = None
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class RAGChain:
    """
    RAG Chain

    業務邏輯：
    1. 接收使用者問題
    2. 檢索相關文件片段
    3. 構建包含上下文的 prompt
    4. 呼叫 LLM 生成答案
    5. 解析並返回答案和來源

    Prompt 結構：
    - 系統指示：定義 AI 的角色和行為
    - 上下文：檢索到的相關文件
    - 對話歷史：之前的對話（可選）
    - 使用者問題：當前問題
    """

    # 系統提示模板 (優化版)
    SYSTEM_PROMPT_TEMPLATE = """你是一個專業的知識庫問答助手。請根據提供的文件內容精確回答問題。

## 回答規則

1. **嚴格依據文件**：只使用提供的文件內容回答，絕不編造資訊
2. **明確引用來源**：回答時標註資訊來自哪個文件，格式為 [來源: 文件名]
3. **結構化回答**：
   - 先直接回答問題的核心
   - 再補充相關細節和背景
   - 如有多個要點，使用條列式呈現
4. **坦承不知**：如果文件中確實沒有相關資訊，請回答「根據目前的文件內容，尚無法找到關於此問題的資訊」
5. **語言匹配**：使用與問題相同的語言回答

當前時間：{current_time}
"""

    # 上下文模板 (優化版)
    CONTEXT_TEMPLATE = """## 參考文件內容

以下是與您問題最相關的文件片段，請仔細閱讀後回答：

{contexts}

---
請根據以上內容回答問題。
"""

    # 單個文件片段模板 (優化版)
    CHUNK_TEMPLATE = """### 📄 {filename}
```
{content}
```
"""

    def __init__(
        self,
        retriever: RetrieverService = None,
        llm_service: BaseLLMService = None,
        top_k: int = None
    ):
        """
        初始化 RAG Chain

        Args:
            retriever: 檢索服務
            llm_service: LLM 服務
            top_k: 檢索數量
        """
        self.retriever = retriever or retriever_service
        self.llm = llm_service or get_llm_service()
        self.top_k = top_k or settings.TOP_K_RETRIEVAL

    async def query(
        self,
        question: str,
        group_id: int,
        document_ids: Optional[List[int]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = None,
        llm_provider: str = None
    ) -> RAGResponse:
        """
        執行 RAG 查詢

        Args:
            question: 使用者問題
            group_id: 群組 ID
            document_ids: 限制在這些文件中搜尋（可選）
            conversation_history: 對話歷史（可選）
            top_k: 檢索數量（覆蓋預設值）
            llm_provider: LLM 提供者（覆蓋預設值）

        Returns:
            RAGResponse: RAG 回應
        """
        k = top_k or self.top_k
        retrieval_results = []

        # 1. 嘗試檢索相關文件
        try:
            if document_ids:
                retrieval_results = await self.retriever.retrieve_for_documents(
                    query=question,
                    document_ids=document_ids,
                    top_k=k
                )
            else:
                retrieval_results = await self.retriever.retrieve_for_group(
                    query=question,
                    group_id=group_id,
                    top_k=k
                )
        except Exception as e:
            # 如果檢索失敗（如 Ollama 未啟動），直接使用 LLM
            import logging
            logging.warning(f"RAG retrieval failed, using direct LLM: {e}")
            retrieval_results = []

        # 2. 構建上下文
        context = self._build_context(retrieval_results)

        # 3. 構建訊息
        messages = self._build_messages(
            question=question,
            context=context,
            conversation_history=conversation_history
        )

        # 4. 選擇 LLM
        llm = get_llm_service(llm_provider) if llm_provider else self.llm

        # 5. 呼叫 LLM
        llm_response = await llm.chat(messages)

        # 6. 構建來源資訊
        sources = [
            {
                "document_id": r.document_id,
                "document_name": r.document_name,
                "chunk_index": r.chunk_index,
                "content": r.content[:200] + "..." if len(r.content) > 200 else r.content,
                "score": round(r.score, 3)
            }
            for r in retrieval_results
        ]

        # 7. 計算信心分數（基於檢索分數）
        confidence = 0.0
        if retrieval_results:
            confidence = sum(r.score for r in retrieval_results) / len(retrieval_results)

        return RAGResponse(
            answer=llm_response.content,
            sources=sources,
            model=llm_response.model,
            retrieval_count=len(retrieval_results),
            generation_time=llm_response.generation_time,
            confidence=round(confidence, 3),
            metadata={
                "prompt_tokens": llm_response.prompt_tokens,
                "completion_tokens": llm_response.completion_tokens,
                "total_tokens": llm_response.total_tokens
            }
        )

    def _build_context(self, retrieval_results: List[RetrievalResult]) -> str:
        """構建上下文文本"""
        if not retrieval_results:
            return ""

        chunks = []
        for r in retrieval_results:
            chunk_text = self.CHUNK_TEMPLATE.format(
                filename=r.document_name or f"Document {r.document_id}",
                content=r.content
            )
            chunks.append(chunk_text)

        contexts = "\n".join(chunks)
        return self.CONTEXT_TEMPLATE.format(contexts=contexts)

    def _build_messages(
        self,
        question: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> List[Message]:
        """構建 LLM 訊息"""
        messages = []

        # 系統提示
        system_prompt = self.SYSTEM_PROMPT_TEMPLATE.format(
            current_time=datetime.now().strftime("%Y-%m-%d %H:%M")
        )
        messages.append(Message(role="system", content=system_prompt))

        # 上下文
        if context:
            messages.append(Message(role="user", content=context))
            messages.append(Message(role="assistant", content="我已閱讀以上文件內容，請提出您的問題。"))

        # 對話歷史
        if conversation_history:
            for msg in conversation_history[-6:]:  # 最多保留最近 3 輪對話
                messages.append(Message(
                    role=msg["role"],
                    content=msg["content"]
                ))

        # 當前問題
        messages.append(Message(role="user", content=question))

        return messages

    async def query_stream(
        self,
        question: str,
        group_id: int,
        document_ids: Optional[List[int]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: int = None,
        llm_provider: str = None
    ):
        """
        串流式 RAG 查詢

        與 query() 相同，但串流返回答案
        用於即時顯示生成內容
        """
        k = top_k or self.top_k

        # 1-3: 與 query() 相同
        if document_ids:
            retrieval_results = await self.retriever.retrieve_for_documents(
                query=question,
                document_ids=document_ids,
                top_k=k
            )
        else:
            retrieval_results = await self.retriever.retrieve_for_group(
                query=question,
                group_id=group_id,
                top_k=k
            )

        context = self._build_context(retrieval_results)
        messages = self._build_messages(question, context, conversation_history)

        # 4. 選擇 LLM 並串流生成
        llm = get_llm_service(llm_provider) if llm_provider else self.llm

        # 構建完整 prompt
        full_prompt = "\n".join([m.content for m in messages if m.role == "user"])
        system_prompt = next((m.content for m in messages if m.role == "system"), None)

        # 串流返回
        async for chunk in llm.stream(full_prompt, system_prompt):
            yield chunk

        # 返回來源資訊（作為最終訊息）
        sources = [
            {
                "document_id": r.document_id,
                "document_name": r.document_name,
                "score": round(r.score, 3)
            }
            for r in retrieval_results
        ]
        yield {"type": "sources", "data": sources}


# 單例實例
rag_chain = RAGChain()
