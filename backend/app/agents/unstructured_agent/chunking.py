# PURPOSE: Splits large text into overlapping chunks
# Why overlap? So that information near chunk boundaries isn't lost
# Example: chunk_size=500, overlap=50
#   Chunk 1: chars 0-500
#   Chunk 2: chars 450-950   (50-char overlap keeps context)
#   Chunk 3: chars 900-1400

from typing import List

class ChunkingAgent:

    def __init__(self, chunk_size: int = 500, overlap: int = 50):
        self.chunk_size = chunk_size
        self.overlap    = overlap

    def chunk(self, text: str) -> List[str]:
        if not text:
            return []

        chunks = []
        start  = 0

        while start < len(text):
            end = start + self.chunk_size

            # Try to end at a sentence boundary (. ! ?) for cleaner chunks
            if end < len(text):
                for punct in [".", "!", "?"]:
                    last_punct = text.rfind(punct, start, end)
                    if last_punct != -1:
                        end = last_punct + 1
                        break

            chunk = text[start:end].strip()
            if len(chunk) > 50:   # ignore tiny fragments
                chunks.append(chunk)

            start = end - self.overlap  # back up by overlap amount

        return chunks

    def chunk_with_metadata(self, text: str, doc_id: int) -> List[dict]:
        # Returns chunks WITH their metadata for Pinecone
        chunks = self.chunk(text)
        return [
            {
                "id":          f"doc{doc_id}_chunk{i}",
                "text":        chunk,
                "doc_id":      doc_id,
                "chunk_index": i,
                "char_count":  len(chunk)
            }
            for i, chunk in enumerate(chunks)
        ]