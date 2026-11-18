import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL


BACKEND_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BACKEND_ROOT / "knowledge"
load_dotenv(BACKEND_ROOT / ".env")

OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "embeddinggemma"
EMBEDDING_DIMENSION = 768
CHAT_MODEL = "phi3:latest"

# Separate from Lesson 2: rebuilding this collection preserves its index.
COLLECTION_NAME = "lesson3_knowledge"
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
TOP_K = 3

ALLOWED_EXTENSIONS = {".md", ".txt"}
MAX_UPLOAD_BYTES = 1_000_000
CORS_ORIGINS = ["http://localhost:5173"]


@lru_cache(maxsize=1)
def get_db_url() -> URL:
    """Read the password from .env, or ask if it has not been filled in."""
    password = os.getenv("PGPASSWORD") or input("Database password (visible): ")
    return URL.create(
        "postgresql+psycopg",
        username="postgres.rswrwrjccqifgxjiemwh",
        password=password,
        host="aws-0-ap-southeast-2.pooler.supabase.com",
        port=5432,
        database="postgres",
        query={"sslmode": "require", "connect_timeout": "15"},
    )
