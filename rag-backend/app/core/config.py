from typing import Optional
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
                
                # Map YAML structure to flat settings
                settings_dict = {}
                if "model" in config_data:
                    model_conf = config_data["model"]
                    if "embedding" in model_conf:
                        settings_dict["EMBEDDING_MODEL"] = model_conf["embedding"].get("model_name")
                    if "llm" in model_conf:
                        settings_dict["LLM_MODEL"] = model_conf["llm"].get("model_name")
                
                if "vector_db" in config_data:
                    settings_dict["VECTOR_DB_DIR"] = config_data["vector_db"].get("path")
                
                if "splitter" in config_data:
                    settings_dict["CHUNK_SIZE"] = config_data["splitter"].get("chunk_size")
                    settings_dict["CHUNK_OVERLAP"] = config_data["splitter"].get("overlap")
                    
                return cls(**settings_dict)
        return cls()

@lru_cache()
def get_settings():
    return Settings.load_from_yaml()
