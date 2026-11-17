from functools import lru_cache

from langchain_ollama import OllamaEmbeddings
from langchain_postgres.vectorstores import DistanceStrategy, PGVector
from sqlalchemy import create_engine

from config import (
    COLLECTION_NAME, EMBEDDING_DIMENSION, EMBEDDING_MODEL,
    OLLAMA_BASE_URL, get_db_url,
)


@lru_cache(maxsize=1)
def get_engine():
    return create_engine(
        get_db_url(),
        connect_args={"sslmode": "require", "connect_timeout": 15},
    )


def get_vector_store(recreate: bool = False) -> PGVector:
    return PGVector(
        embeddings=OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL),
        connection=get_engine(),
        collection_name=COLLECTION_NAME,
        embedding_length=EMBEDDING_DIMENSION,
        distance_strategy=DistanceStrategy.COSINE,
        use_jsonb=True,
        pre_delete_collection=recreate,
        create_extension=False,  # pgvector уже включён в Supabase.
    )
