import os
import uuid
import shutil
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings
from app.utils.doc_parser import DocParser
from app.schemas.doc import UploadResponse, DocItem
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

DOCS_METADATA = []

class DocService:
    @staticmethod
    async def process_doc(file: UploadFile) -> UploadResponse:
        # 1. Save File
        if not os.path.exists(settings.UPLOAD_DIR):
            os.makedirs(settings.UPLOAD_DIR)
        
        file_ext = os.path.splitext(file.filename)[1].lower()
        doc_id = str(uuid.uuid4())
        safe_filename = f"{doc_id}_{file.filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)
        
        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            logger.error(f"File save error: {e}")
            raise HTTPException(status_code=500, detail="File save failed")

        # 2. Parse Content
        try:
            content = DocParser.parse(file_path)
            if not content:
                raise ValueError("Empty content")
        except Exception as e:
            logger.error(f"Parse error: {e}")
            raise HTTPException(status_code=400, detail=f"File parse failed: {str(e)}")

        # 3. Split Text
        chunks = DocService._split_text(content, file_ext)
        logger.info(f"Generated {len(chunks)} chunks for {file.filename}")

        # 4. Vectorize & Store
        vector_status = "解析成功(未向量化)"
        try:
            if settings.DASHSCOPE_API_KEY:
                embeddings = DashScopeEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    dashscope_api_key=settings.DASHSCOPE_API_KEY
                )
                DocService._add_to_vector_store(chunks, embeddings)
                vector_status = "已索引"
            else:
                logger.warning("No DASHSCOPE_API_KEY found. Skipping vectorization.")
        except Exception as e:
            logger.error(f"Vectorization error: {e}")
            vector_status = "向量化失败"

        # 5. Update Metadata
        doc_meta = {
            "id": doc_id,
            "name": file.filename,
            "upload_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": vector_status,
            "size": os.path.getsize(file_path),
            "path": file_path
        }
        DOCS_METADATA.append(doc_meta)

        return UploadResponse(
            status="success",
            doc_id=doc_id,
            length=len(content),
            message="Document processed successfully"
        )

    @staticmethod
    def _split_text(content: str, ext: str) -> list[Document]:
        if ext in [".md", ".markdown"]:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            md_header_splits = markdown_splitter.split_text(content)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            return text_splitter.split_documents(md_header_splits)
        else:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=settings.CHUNK_SIZE,
                chunk_overlap=settings.CHUNK_OVERLAP
            )
            return text_splitter.create_documents([content])

    @staticmethod
    def _add_to_vector_store(chunks, embeddings):
        if not os.path.exists(settings.VECTOR_DB_DIR):
            os.makedirs(settings.VECTOR_DB_DIR)
            
        index_file = os.path.join(settings.VECTOR_DB_DIR, "index.faiss")
        
        if os.path.exists(index_file):
            try:
                vs = FAISS.load_local(settings.VECTOR_DB_DIR, embeddings, allow_dangerous_deserialization=True)
                vs.add_documents(chunks)
                vs.save_local(settings.VECTOR_DB_DIR)
            except Exception as e:
                logger.error(f"Failed to load vector store: {e}")
                # Fallback to create new if load fails
                vs = FAISS.from_documents(chunks, embeddings)
                vs.save_local(settings.VECTOR_DB_DIR)
        else:
            vs = FAISS.from_documents(chunks, embeddings)
            vs.save_local(settings.VECTOR_DB_DIR)

    @staticmethod
    def get_doc_list() -> list[DocItem]:
        try:
            return [DocItem(**item) for item in DOCS_METADATA]
        except Exception as e:
            logger.error(f"Error getting doc list: {e}")
            return []
