from fastapi import APIRouter

router = APIRouter()

@router.post("/query")
async def query_document():
    return {"message": "Query endpoint placeholder"}
