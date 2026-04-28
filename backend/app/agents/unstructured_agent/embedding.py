# PURPOSE: Converts text chunks into vectors and stores them in Pinecone
#
# What is a vector?
# A text like "quarterly revenue grew 15%" becomes a list of 1536 floats
# like [0.023, -0.451, 0.891, ...] that represents its MEANING mathematically
#
# Similar meanings → similar vectors → can be searched by similarity

from pydantic import SecretStr
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
from typing import List, Dict
from config import settings

class EmbeddingAgent:

    def __init__(self):
        # OpenAI client for creating embeddings
        self.openai = OpenAI(
            api_key=settings.OPENAI_API_KEY.get_secret_value()
            )

        # Pinecone client for storing vectors
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)

        # Connect to (or create) the Pinecone index
        existing = [idx.name for idx in pc.list_indexes()]
        if settings.PINECONE_INDEX_NAME not in existing:
            pc.create_index(
                name=settings.PINECONE_INDEX_NAME,
                dimension=settings.PINECONE_DIMENSION,  # 1536 for ada-002
                metric="cosine",                         # cosine similarity
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )

        self.index = pc.Index(settings.PINECONE_INDEX_NAME)

    def embed_text(self, text: str) -> List[float]:
        # Convert one piece of text into a vector
        response = self.openai.embeddings.create(
            model="text-embedding-ada-002",
            # ada-002 = OpenAI's embedding model
            # Always produces 1536-dimensional vectors
            input=text
        )
        return response.data[0].embedding  # the list of 1536 floats

    def upsert_chunks(self, chunks: List[Dict]) -> int:
        # chunks = list of {"id": "doc1_chunk0", "text": "...", "doc_id": 1, ...}

        vectors = []
        for chunk in chunks:
            embedding = self.embed_text(chunk["text"])
            vectors.append({
                "id":     chunk["id"],
                "values": embedding,
                "metadata": {
                    # Metadata stored alongside the vector
                    # Retrieved WITH the vector during search
                    "doc_id":      chunk["doc_id"],
                    "chunk_index": chunk["chunk_index"],
                    "text":        chunk["text"][:1000]
                    # store first 1000 chars (Pinecone metadata limit)
                }
            })

        # Upsert in batches of 100 (Pinecone recommendation)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)

        return len(vectors)