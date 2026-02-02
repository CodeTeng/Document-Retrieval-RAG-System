from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.doc_service import DocService
from app.schemas.doc import UploadResponse, DocItem
from typing import List

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    文档上传与解析接口
    """
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    
    # Simple extension check
    allowed_exts = [".pdf", ".docx", ".doc", ".md", ".markdown", ".txt"]
    import os
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_exts:
        raise HTTPException(status_code=400, detail=f"Unsupported file format. Allowed: {allowed_exts}")

    return await DocService.process_doc(file)

@router.get("/docs/list", response_model=List[DocItem])
async def list_documents():
    """
    获取已上传文档列表
    """
    return DocService.get_doc_list()
