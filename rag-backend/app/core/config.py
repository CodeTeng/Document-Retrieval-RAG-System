import os
import yaml
from pydantic import BaseModel
from typing import Optional

class ServerConfig(BaseModel):
    host: str
    port: int
    upload_max_size: int
    request_timeout: int

class ModelConfig(BaseModel):
    provider: str
    model_name: str
    api_key_env: str
    temperature: Optional[float] = 0.7

class VectorDBConfig(BaseModel):
    type: str
    path: str
    similarity_threshold: float
    top_n: int

class SplitterConfig(BaseModel):
    chunk_size: int
    overlap: int

class AppConfig(BaseModel):
    server: ServerConfig
    model: dict # Simplified for now, can be nested
    vector_db: VectorDBConfig
    splitter: SplitterConfig

class Settings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.load_config()
        return cls._instance

    def load_config(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config", "app.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config_data = yaml.safe_load(f)
        
        self.server = ServerConfig(**self.config_data['server'])
        self.vector_db = VectorDBConfig(**self.config_data['vector_db'])
        self.splitter = SplitterConfig(**self.config_data['splitter'])
        # Simplified model config access
        self.model_embedding = self.config_data['model']['embedding']
        self.model_llm = self.config_data['model']['llm']

settings = Settings()
