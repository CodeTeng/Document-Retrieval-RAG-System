import json
import logging
import os
from typing import Generator
from app.core.config import get_settings
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from dashscope import Generation
from http import HTTPStatus

settings = get_settings()
logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    def chat_stream(question: str, top_k: int = 3) -> Generator[str, None, None]:
        """
        Streaming chat generation with RAG
        Yields JSON strings:
        - {"step": "init", "message": "..."}
        - {"step": "retrieving", "message": "..."}
        - {"step": "retrieved", "data": [...], "message": "..."}
        - {"step": "generating", "message": "..."}
        - {"step": "answer", "data": "...", "done": False}
        - {"step": "completed", "message": "...", "done": True}
        - {"step": "error", "message": "..."}
        """
        # Step 1: Initialize
        yield json.dumps({"step": "init", "message": "正在初始化问答服务..."}) + "\n"
        
        try:
            # Step 2: Load Vector Store
            yield json.dumps({"step": "retrieving", "message": "正在加载知识库..."}) + "\n"
            
            if not settings.DASHSCOPE_API_KEY:
                yield json.dumps({"step": "error", "message": "未配置API Key"}) + "\n"
                return

            # Check if vector db exists
            if not os.path.exists(settings.VECTOR_DB_DIR) or not os.listdir(settings.VECTOR_DB_DIR):
                 # Auto-rebuild check
                 from app.services.doc_service import DocService, DOCS_METADATA
                 indexed_docs = [d for d in DOCS_METADATA if d.get("status") == "已索引"]
                 
                 if indexed_docs:
                     yield json.dumps({"step": "retrieving", "message": "检测到索引丢失，正在尝试重建..."}) + "\n"
                     try:
                         # Trigger sync rebuild for immediate use
                         # Note: Rebuild might be slow, but better than error
                         # For this specific flow, we'll try to rebuild in-place or fail
                         DocService.rebuild_index() 
                         
                         if not os.path.exists(settings.VECTOR_DB_DIR) or not os.listdir(settings.VECTOR_DB_DIR):
                             yield json.dumps({"step": "error", "message": "知识库重建失败，请重新上传文档"}) + "\n"
                             return
                     except Exception as e:
                         yield json.dumps({"step": "error", "message": f"重建索引异常: {e}"}) + "\n"
                         return
                 else:
                     yield json.dumps({"step": "error", "message": "知识库为空，请先上传文档"}) + "\n"
                     return

            embeddings = DashScopeEmbeddings(
                model=settings.EMBEDDING_MODEL,
                dashscope_api_key=settings.DASHSCOPE_API_KEY
            )
            
            try:
                # Allow dangerous deserialization as we trust our own data
                vector_store = FAISS.load_local(
                    settings.VECTOR_DB_DIR, 
                    embeddings,
                    allow_dangerous_deserialization=True
                )
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                yield json.dumps({"step": "error", "message": f"知识库加载失败: {str(e)}"}) + "\n"
                return

            # Step 3: Search
            yield json.dumps({"step": "retrieving", "message": f"正在检索相关文档 (Top {top_k})..."}) + "\n"
            
            # Sync search is fine as this generator runs in a thread
            docs = vector_store.similarity_search_with_score(question, k=top_k)
            
            relevant_content = []
            sources = []
            for doc, score in docs:
                # Score: lower is better for L2
                relevant_content.append(doc.page_content)
                sources.append({
                    "content": doc.page_content[:200] + "...", 
                    "score": float(score), 
                    "source": doc.metadata.get("name", "unknown"),
                    "page": doc.metadata.get("page", 0)
                })
            
            yield json.dumps({"step": "retrieved", "data": sources, "message": f"检索到 {len(docs)} 个相关片段"}) + "\n"
            
            if not relevant_content:
                yield json.dumps({"step": "answer", "data": "很抱歉，在现有知识库中未找到与您问题相关的答案。建议您：\n1. 尝试更换关键词\n2. 确认已上传相关文档\n3. 检查问题描述是否准确", "done": True}) + "\n"
                return

            # Step 4: Generate Answer
            yield json.dumps({"step": "generating", "message": "正在生成回答..."}) + "\n"
            
            context = "\n\n".join(relevant_content)
            prompt = f"请基于以下参考内容回答用户的问题。如果参考内容不足以回答，请委婉告知用户并说明原因。不要编造事实。\n\n参考内容：\n{context}\n\n用户问题：{question}"
            
            # Call DashScope
            responses = Generation.call(
                model=settings.LLM_MODEL,
                prompt=prompt,
                api_key=settings.DASHSCOPE_API_KEY,
                stream=True,
                result_format='message'
            )
            
            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    content = response.output.choices[0].message.content
                    # DashScope stream returns full content so far
                    yield json.dumps({"step": "answer", "data": content, "done": False}) + "\n"
                else:
                    yield json.dumps({"step": "error", "message": f"模型调用失败: {response.message}"}) + "\n"
            
            yield json.dumps({"step": "completed", "message": "回答完成", "done": True}) + "\n"

        except Exception as e:
            logger.error(f"Chat error: {e}")
            yield json.dumps({"step": "error", "message": f"系统异常: {str(e)}"}) + "\n"
