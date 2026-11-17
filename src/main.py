import ollama

response = ollama.embed(
    model='embeddinggemma',
    input= ['The door is open.', 'The door is closed.']
)

a = response.embeddings[0]
b = response.embeddings[1]

multiply = sum(x * y for x, y in zip(a, b))
length_a = sum(x ** 2 for x in a)
length_b = sum(y ** 2 for y in b)
result = multiply / ((length_a ** 0.5) * (length_b ** 0.5))
print(result)