import numpy as np
import ollama

MODEL = "embeddinggemma"


def get_embedding(text: str) -> np.ndarray:
    # Отправляем один текст в Ollama и получаем его embedding.
    response = ollama.embed(model=MODEL, input=text)

    # Берём первый вектор и превращаем его в массив NumPy.
    return np.array(response["embeddings"][0], dtype=np.float32)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    # Скалярное произведение делим на произведение длин векторов.
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


text_a = "A dog is running through the park."
text_b = "A puppy is running outside."
text_c = "PostgreSQL supports database transactions."

# Каждый вызов получает вектор для одного текста.
embedding_a = get_embedding(text_a)
embedding_b = get_embedding(text_b)
embedding_c = get_embedding(text_c)

print("A:", text_a)
print("B:", text_b)
print("C:", text_c)
print()
print("A vs B (dog / puppy):", cosine_similarity(embedding_a, embedding_b))
print("A vs C (dog / database):", cosine_similarity(embedding_a, embedding_c))
