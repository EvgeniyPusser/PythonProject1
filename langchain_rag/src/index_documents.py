import argparse
from uuid import NAMESPACE_URL, uuid5

from config import COLLECTION_NAME
from knowledge import load_documents, split_documents
from vector_store import get_engine, get_vector_store


def main():
    parser = argparse.ArgumentParser(description="Index company Markdown documents")
    parser.add_argument(
        "--recreate", action="store_true",
        help="Delete and rebuild only the configured LangChain collection",
    )
    args = parser.parse_args()
    documents = load_documents()
    chunks = split_documents(documents)
    print(f"Loaded {len(documents)} documents.", flush=True)
    print(f"Created {len(chunks)} chunks.", flush=True)
    if not chunks:
        parser.error("No document chunks found")

    # Повторная загрузка тех же фрагментов обновляет их, не создавая копий.
    ids = [
        str(uuid5(NAMESPACE_URL,
                  f"{COLLECTION_NAME}:{chunk.metadata['source']}:"
                  f"{chunk.metadata['start_index']}:{chunk.page_content}"))
        for chunk in chunks
    ]
    try:
        store = get_vector_store(recreate=args.recreate)
        stored_ids = store.add_documents(documents=chunks, ids=ids)
        print(f"Indexed {len(stored_ids)} chunks.")
    finally:
        if get_engine.cache_info().currsize:
            get_engine().dispose()


if __name__ == "__main__":
    main()
