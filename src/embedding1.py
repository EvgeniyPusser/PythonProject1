import ollama

MODEL = "embeddinggemma"

text = "Python supports asynchronous programming with asyncio."

response = ollama.embed(
    model=MODEL,
    input=text,
)

embedding = response.embeddings[0]

print(type(embedding))
print("Dimensions:", len(embedding))
print("First 10 values:")
print(embedding[:10])
