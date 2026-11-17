import ollama
from pgvector import Vector
from pgvector.psycopg import register_vector

from connect_db import connect

MODEL = "embeddinggemma"


def create_embedding(text: str) -> Vector:
    response = ollama.embed(model=MODEL, input=text)
    return Vector(response.embeddings[0])


def semantic_search(query: str, password: str, limit: int = 3):
    # Превращаем вопрос в вектор той же моделью, что и документы.
    embedding = create_embedding(query)

    with connect(password) as connection:
        register_vector(connection)
        result = connection.execute(
            """
            SELECT title, content,
                   1 - (embedding <=> %s) AS similarity
            FROM documents
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (embedding, embedding, limit),
        )
        return result.fetchall()


def main():
    password = input("Database password (visible): ")
    query = (
        "How can a Python program do other work "
        "while waiting for network operations?"
    )
    results = semantic_search(query, password)

    print(f"\nQuery: {query}\n")
    for index, (title, content, similarity) in enumerate(results, start=1):
        print(f"{index}. {title} | similarity: {similarity:.4f}")
        print(content)
        print()


if __name__ == "__main__":
    main()
