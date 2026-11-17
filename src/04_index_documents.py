import ollama
from pgvector import Vector
from pgvector.psycopg import register_vector

from connect_db import connect

MODEL = "embeddinggemma"

# Учебные документы: заголовок и текст каждого документа.
documents = [
    {
        "title": "Python asyncio",
        "content": (
            "Python's asyncio library coordinates coroutines "
            "using an event loop. Tasks can yield control while "
            "waiting for I/O, allowing other tasks to run."
        ),
    },
    {
        "title": "JavaScript Event Loop",
        "content": (
            "JavaScript uses an event loop to coordinate "
            "asynchronous operations and execute queued callbacks."
        ),
    },
    {
        "title": "FastAPI",
        "content": (
            "FastAPI is a Python framework for building web APIs. "
            "It supports asynchronous request handlers using "
            "async and await."
        ),
    },
    {
        "title": "PostgreSQL Transactions",
        "content": (
            "PostgreSQL transactions group multiple database "
            "operations into a single atomic unit of work."
        ),
    },
    {
        "title": "PostgreSQL Indexes",
        "content": (
            "Database indexes can improve query performance by "
            "allowing PostgreSQL to find rows without scanning "
            "the entire table."
        ),
    },
]


def main():
    password = input("Database password (visible): ")

    # Для каждого текста Ollama создаёт вектор из 768 чисел.
    embeddings = []
    for document in documents:
        response = ollama.embed(model=MODEL, input=document["content"])
        embedding = response.embeddings[0]
        if len(embedding) != 768:
            raise ValueError(f"Expected 768 dimensions, got {len(embedding)}")
        embeddings.append(embedding)
        print("Embedded:", document["title"], flush=True)

    with connect(password) as connection:
        register_vector(connection)
        inserted = 0
        for document, embedding in zip(documents, embeddings):
            # Повторный запуск не добавляет копию того же заголовка и текста.
            cursor = connection.execute(
                """
                INSERT INTO documents (title, content, embedding)
                SELECT %s, %s, %s
                WHERE NOT EXISTS (
                    SELECT 1 FROM documents WHERE title = %s AND content = %s
                )
                """,
                (
                    document["title"], document["content"], Vector(embedding),
                    document["title"], document["content"],
                ),
            )
            inserted += cursor.rowcount
        # Выход из with сохраняет все вставки одной транзакцией.
    print("Inserted documents:", inserted)


if __name__ == "__main__":
    main()
