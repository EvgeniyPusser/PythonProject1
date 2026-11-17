import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import URL

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge"
load_dotenv(PROJECT_ROOT / ".env")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "embeddinggemma")
EMBEDDING_DIMENSION = 768
# В .env выбрана установленная phi3; для модели из урока укажи gemma3:4b.
CHAT_MODEL = os.getenv("CHAT_MODEL", "phi3:latest")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "lesson2_langchain")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "600"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))
TOP_K = int(os.getenv("TOP_K", "3"))


def get_db_url() -> URL:
    password = os.getenv("PGPASSWORD") or input("Database password (visible): ")
    # Пароль передаём отдельно, чтобы символы @ и & не ломали адрес.
    return URL.create(
        "postgresql+psycopg",
        username=os.getenv("PGUSER", "postgres.rswrwrjccqifgxjiemwh"),
        password=password,
        host=os.getenv("PGHOST", "aws-0-ap-southeast-2.pooler.supabase.com"),
        port=int(os.getenv("PGPORT", "5432")),
        database=os.getenv("PGDATABASE", "postgres"),
    )
