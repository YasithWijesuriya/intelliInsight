# PURPOSE: Converts text chunks into vectors and stores them in Pinecone
#
# What is a vector?
# A text like "quarterly revenue grew 15%" becomes a list of 1536 floats
# like [0.023, -0.451, 0.891, ...] that represents its MEANING mathematically
#
# Similar meanings → similar vectors → can be searched by similarity

from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from typing import List, Dict
from app.config import settings

class EmbeddingAgent:

    def __init__(self):
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())

        pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        existing = [idx.name for idx in pc.list_indexes()]
        if settings.PINECONE_INDEX_NAME not in existing:
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.PINECONE_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.index = pc.Index(settings.PINECONE_INDEX_NAME)

    def embed_text(self, text: str) -> List[float]:
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding

    def upsert_chunks(self, chunks: List[Dict]) -> int:
        if not chunks:
            return 0

        vectors = []  # this will hold the final data we send to Pinecone (Volatile temporary memory)
        for chunk in chunks:
            embedding = self.embed_text(chunk["text"])
            vectors.append({
                "id":     chunk["id"],
                "values": embedding,
                "metadata": {

                    "doc_id":      chunk["doc_id"],
                    "document_id": chunk["doc_id"],   # kept for compatibility
                    "chunk_index": chunk["chunk_index"],
                    "text":        chunk["text"][:1000]
                }
            })

        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

        return len(vectors)
    
    # id	Unique ID of SINGLE chunk/vector
    # doc_id	ID of WHOLE document


    #!why we use batch_size?
# Batch size controls how many vectors are sent to Pinecone in ONE request.
# Instead of uploading vectors one-by-one (slow and many API calls),
# we upload them in groups for better performance and efficiency.
#
# Example:
# If total vectors = 250 and batch_size = 100
#
# Batch 1 -> vectors[0:100]
# Batch 2 -> vectors[100:200]
# Batch 3 -> vectors[200:250]
#
# This approach reduces:
# - network overhead
# - API requests
# - upload time
