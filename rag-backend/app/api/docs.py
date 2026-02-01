from fastapi import APIRouter

router = APIRouter()

@router.post("/upload")
async def upload_document():
    return {"message": "Upload endpoint placeholder"}

@router.get("/docs/list")
async def list_documents():
    return {"message": "List documents endpoint placeholder"}
