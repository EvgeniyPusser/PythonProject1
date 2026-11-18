from functools import lru_cache

from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import DistanceStrategy, PGVector
from sqlalchemy import Engine, create_engine

from .config import (
    COLLECTION_NAME,
    EMBEDDING_DIMENSION,
    EMBEDDING_MODEL,
    OLLAMA_BASE_URL,
    get_db_url,
)


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(get_db_url(), pool_pre_ping=True)


def get_vector_store(recreate: bool = False) -> PGVector:
    return PGVector(
        embeddings=OllamaEmbeddings(
            model=EMBEDDING_MODEL,
            base_url=OLLAMA_BASE_URL,
        ),
        connection=get_engine(),
        collection_name=COLLECTION_NAME,
        embedding_length=EMBEDDING_DIMENSION,
        distance_strategy=DistanceStrategy.COSINE,
        use_jsonb=True,
        pre_delete_collection=recreate,
        create_extension=False,  # pgvector is already enabled in Supabase.
    )
