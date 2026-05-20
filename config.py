from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    llm_provider: str = "openai"          # openai | anthropic
    embed_model: str = "text-embedding-3-small"
    chat_model: str = "gpt-4o"
    upload_dir: str = "uploads"
    faiss_index_path: str = "faiss_index"
    max_file_size_mb: int = 20
    chunk_size: int = 800
    chunk_overlap: int = 100
    top_k: int = 5

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
