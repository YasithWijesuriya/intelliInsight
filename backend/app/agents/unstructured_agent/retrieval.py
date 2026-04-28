# PURPOSE: Semantic search — finds the most relevant chunks for a question
# How it works:
# 1. Embed the user's question into a vector
# 2. Search Pinecone for the closest matching vectors
# 3. Return the text content of those chunks

from urllib import response

from pinecone import Pinecone
from openai import OpenAI
from typing import List, Dict, Optional
from app.config import settings

class RetrievalAgent:

    def __init__(self):
        self.openai = OpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())
        pc          = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index  = pc.Index(settings.PINECONE_INDEX_NAME)

    def retrieve(self, query: str, top_k: int = 5,
                 doc_id: Optional[int] = None) -> List[Dict]:

        # Step 1: Embed the query the SAME WAY we embedded documents
        # (must use same model so the vector spaces match)
        response = self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_vector = response.data[0].embedding  #! Convert user query into a vector (list of numbers). The API returns the result inside a list, so we take the first item [0] and extract its embedding.

        # Step 2: Build optional filter to search within one document
        filter_dict = ({"doc_id": {"$eq": doc_id}} if doc_id is not None else None)        # $eq = equals

        # Step 3: Search Pinecone
        results = self.index.query(
            vector=query_vector,
            top_k=top_k,          # return top 5 closest chunks
            include_metadata=True, # include the text content
            filter=filter_dict #type: ignore
        )

        # Step 4: Return chunks sorted by relevance score
        return [
            {
                "text":         match.metadata.get("text", ""),
                "score":        round(match.score, 3),
                # score = cosine similarity (0 to 1, higher = more relevant)
                "doc_id":       match.metadata.get("doc_id"),
                "chunk_index":  match.metadata.get("chunk_index"),
                "pinecone_id":  match.id
            }
            for match in results.matches #type: ignore
            #! So who created matches? Pinecone system itself
            # Pinecone internally builds a response like this:

            #         {
            #             "matches": [
            #                       {...},{...}
            #                       ],
            #             "namespace": "",
            #             "usage": {...}
            #         }
            if match.score > 0.7   # only return relevant results (>70% match)
        ]