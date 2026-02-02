import os
import uuid
import shutil
import json
from datetime import datetime
from fastapi import UploadFile, HTTPException
from app.core.config import get_settings
from app.utils.doc_parser import DocParser
from app.schemas.doc import UploadResponse, DocItem, DocListResponse
from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

METADATA_FILE = os.path.join(settings.UPLOAD_DIR, "metadata.json")

def load_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load metadata: {e}")
            return []
    return []

def save_metadata(metadata):
    try:
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to save metadata: {e}")

DOCS_METADATA = load_metadata()

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
        save_metadata(DOCS_METADATA)

        return UploadResponse(
            status="success",
            doc_id=doc_id,
            length=len(content),
            message="Document processed successfully"
        )

    from fastapi import BackgroundTasks

    @staticmethod
    def rebuild_index():
        """Rebuilds the vector index from scratch."""
        try:
            logger.info("Starting background index rebuild...")
            
            # Reload metadata to ensure it's fresh
            current_metadata = load_metadata()
            
            # Clear vector store directory
            if os.path.exists(settings.VECTOR_DB_DIR):
                try:
                    shutil.rmtree(settings.VECTOR_DB_DIR)
                except Exception as e:
                    logger.warning(f"Failed to clean vector db dir: {e}")
            
            # Re-add all existing docs
            all_chunks = []
            valid_count = 0
            
            if settings.DASHSCOPE_API_KEY:
                embeddings = DashScopeEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    dashscope_api_key=settings.DASHSCOPE_API_KEY
                )
                
                for d in current_metadata:
                    # Index documents that are marked as indexed or ready
                    if d.get("status") in ["已索引", "解析成功(未向量化)"]:
                        file_path = d["path"]
                        # Ensure absolute path check if relative fails
                        if not os.path.exists(file_path):
                             file_path = os.path.abspath(file_path)
                             
                        if os.path.exists(file_path):
                            try:
                                logger.info(f"Processing {d['name']} for index...")
                                content = DocParser.parse(file_path)
                                ext = os.path.splitext(d["name"])[1].lower()
                                chunks = DocService._split_text(content, ext)
                                all_chunks.extend(chunks)
                                valid_count += 1
                            except Exception as e:
                                logger.error(f"Failed to process {d['name']}: {e}")
                        else:
                            logger.error(f"File not found during rebuild: {file_path}")
                
                if all_chunks:
                    logger.info(f"Vectorizing {len(all_chunks)} chunks from {valid_count} documents...")
                    DocService._add_to_vector_store(all_chunks, embeddings)
                else:
                    logger.warning("No chunks available to index.")
            else:
                logger.warning("Missing API KEY, cannot rebuild index.")
                
            logger.info("Background index rebuild completed.")
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")

    @staticmethod
    def delete_doc(doc_id: str, background_tasks: BackgroundTasks) -> bool:
        # 1. Find doc
        doc = next((d for d in DOCS_METADATA if d["id"] == doc_id), None)
        if not doc:
            return False
            
        # 2. Delete file
        file_path = doc.get("path")
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                logger.error(f"Failed to delete file {file_path}: {e}")
                
        # 3. Remove from metadata
        DOCS_METADATA.remove(doc)
        save_metadata(DOCS_METADATA)
        
        # 4. Trigger Async Rebuild
        background_tasks.add_task(DocService.rebuild_index)

        return True

    @staticmethod
    def get_doc_path(doc_id: str) -> str:
        doc = next((d for d in DOCS_METADATA if d["id"] == doc_id), None)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        file_path = doc.get("path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        return file_path

    @staticmethod
    def get_doc_content(doc_id: str) -> str:
        doc = next((d for d in DOCS_METADATA if d["id"] == doc_id), None)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
            
        file_path = doc.get("path")
        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
            
        try:
            content = DocParser.parse(file_path)
            return content
        except Exception as e:
            logger.error(f"Failed to read doc content: {e}")
            raise HTTPException(status_code=500, detail="Failed to read document content")

    @staticmethod
    def _split_text(text: str, ext: str) -> list[Document]:
        if ext in [".md", ".markdown"]:
            headers_to_split_on = [
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ]
            markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
            md_header_splits = markdown_splitter.split_text(text)
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
            return text_splitter.create_documents([text])

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
    def reindex_doc(doc_id: str) -> bool:
        """
        Re-parse and vectorize an existing document
        """
        # Find doc metadata
        doc_meta = next((d for d in DOCS_METADATA if d["id"] == doc_id), None)
        if not doc_meta:
            logger.error(f"Doc {doc_id} not found")
            return False
            
        file_path = doc_meta["path"]
        if not os.path.exists(file_path):
            logger.error(f"File {file_path} not found")
            return False
            
        try:
            # 1. Parse
            content = DocParser.parse(file_path)
            if not content:
                logger.error("Empty content during reindex")
                return False
                
            # 2. Split
            ext = os.path.splitext(doc_meta["name"])[1].lower()
            chunks = DocService._split_text(content, ext)
            
            # 3. Vectorize
            if settings.DASHSCOPE_API_KEY:
                embeddings = DashScopeEmbeddings(
                    model=settings.EMBEDDING_MODEL,
                    dashscope_api_key=settings.DASHSCOPE_API_KEY
                )
                DocService._add_to_vector_store(chunks, embeddings)
                
                # 4. Update Status
                doc_meta["status"] = "已索引"
                save_metadata(DOCS_METADATA)
                return True
            else:
                logger.warning("No API KEY during reindex")
                return False
                
        except Exception as e:
            logger.error(f"Reindex failed: {e}")
            return False

    @staticmethod
    def sync_docs_from_disk():
        """
        Scan upload directory and sync missing files to metadata
        """
        if not os.path.exists(settings.UPLOAD_DIR):
            return
            
        existing_files = {doc["path"] for doc in DOCS_METADATA}
        updated = False
        
        for filename in os.listdir(settings.UPLOAD_DIR):
            if filename == "metadata.json":
                continue
                
            file_path = os.path.join(settings.UPLOAD_DIR, filename)
            if not os.path.isfile(file_path):
                continue
                
            if file_path not in existing_files:
                # Try to extract original name from UUID_filename format
                parts = filename.split("_", 1)
                original_name = parts[1] if len(parts) > 1 else filename
                doc_id = parts[0] if len(parts) > 1 else str(uuid.uuid4())
                
                doc_meta = {
                    "id": doc_id,
                    "name": original_name,
                    "upload_time": datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%Y-%m-%d %H:%M"),
                    "status": "未索引", # Assume unindexed for recovered files
                    "size": os.path.getsize(file_path),
                    "path": file_path
                }
                DOCS_METADATA.append(doc_meta)
                updated = True
        
        if updated:
            save_metadata(DOCS_METADATA)

    @staticmethod
    def get_doc_list(page: int = 1, size: int = 6, keyword: str = "") -> DocListResponse:
        # Sync before listing
        DocService.sync_docs_from_disk()
        
        try:
            # 1. Filter
            filtered_docs = DOCS_METADATA
            if keyword:
                keyword = keyword.lower()
                filtered_docs = [
                    doc for doc in DOCS_METADATA 
                    if keyword in doc["name"].lower()
                ]
            
            # 2. Sort (newest first)
            filtered_docs.sort(key=lambda x: x["upload_time"], reverse=True)
            
            # 3. Paginate
            total = len(filtered_docs)
            start = (page - 1) * size
            end = start + size
            paginated_docs = filtered_docs[start:end]
            
            return DocListResponse(
                total=total,
                items=[DocItem(**item) for item in paginated_docs],
                page=page,
                size=size
            )
        except Exception as e:
            logger.error(f"Error getting doc list: {e}")
            return DocListResponse(total=0, items=[], page=page, size=size)
