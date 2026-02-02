from typing import List, Optional
from pydantic_settings import BaseSettings
from functools import lru_cache
import yaml
import os

class Settings(BaseSettings):
    # App
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "RAG Backend"
    
    # Storage
    UPLOAD_DIR: str = "data/docs"
    VECTOR_DB_DIR: str = "data/vector_db"
    
    # Model (Alibaba)
    DASHSCOPE_API_KEY: Optional[str] = None
    EMBEDDING_MODEL: str = "text-embedding-v1"
    LLM_MODEL: str = "qwen-turbo"
    
    # RAG
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 50
    TOP_K: int = 3
    SIMILARITY_THRESHOLD: float = 0.7

    class Config:
        env_file = ".env"

    @classmethod
    def load_from_yaml(cls, path: str = "config/app.yaml"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)
                return cls(**config_data)
        return cls()

@lru_cache()
def get_settings():
    # Priority: Env Vars > YAML > Defaults
    # For now, just simple loading
    return Settings()
