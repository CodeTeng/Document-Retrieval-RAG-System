from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import docs, query, config
from app.core.config import settings

app = FastAPI(
    title="RAG Document Retrieval System",
    description="A RAG system for document retrieval and Q&A using Alibaba Cloud models.",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Should be configured properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(docs.router, prefix="/api", tags=["Documents"])
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(config.router, prefix="/api", tags=["Config"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.server.host, port=settings.server.port)
