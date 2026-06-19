import numpy as np
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def load_chunks():
    with open("company_info.txt", "r", encoding="utf-8") as file:
        text = file.read()

    chunks = text.split("\n\n")
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding)


def find_best_context(question):
    chunks = load_chunks()

    question_embedding = get_embedding(question)

    best_chunk = ""
    best_score = -1

    for chunk in chunks:
        chunk_embedding = get_embedding(chunk)

        score = np.dot(question_embedding, chunk_embedding) / (
            np.linalg.norm(question_embedding) * np.linalg.norm(chunk_embedding)
        )

        if score > best_score:
            best_score = score
            best_chunk = chunk

    return best_chunk