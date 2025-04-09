import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""

    # API settings
    API_PREFIX: str = "/api"
    PROJECT_NAME: str = "Movie Recommendation MCP Server"

    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:4200",  # Angular app
        "http://localhost:3000",  # Chainlit
        "http://localhost:7860",  # Gradio
    ]

    # ChromaDB settings
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_db"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"  # SentenceTransformers model

    # LLM settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL_NAME: str = os.getenv("LLM_MODEL_NAME", "gpt-3.5-turbo")
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000

    # Data settings
    MOVIE_DATA_SOURCE: str = os.getenv("MOVIE_DATA_SOURCE",
                                        "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip")
    DATA_DIR: str = "./data"
    PROCESSED_DATA_DIR: str = "./data/processed"

# Create settings instance
settings = Settings()