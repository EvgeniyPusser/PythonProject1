from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE, KNOWLEDGE_DIR


def load_documents() -> list[Document]:
    return [
        Document(
            page_content=path.read_text(encoding="utf-8"),
            metadata={"source": path.name},
        )
        for path in sorted(KNOWLEDGE_DIR.glob("*.md"))
    ]


def split_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(documents)


if __name__ == "__main__":
    documents = load_documents()
    chunks = split_documents(documents)
    print("Documents:", len(documents))
    print("Chunks:", len(chunks))
    for index, chunk in enumerate(chunks, start=1):
        print(f"\nCHUNK {index}")
        print(chunk.metadata)
        print(chunk.page_content)
