from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import docs
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
# Mount under /api
app.include_router(docs.router, prefix="/api", tags=["docs"])

@app.get("/")
async def root():
    return {"message": "RAG Backend Service is running"}
