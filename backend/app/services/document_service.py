# PURPOSE: Orchestrates the full document processing pipeline
# When a PDF is uploaded, this service runs all the agent steps

from sqlalchemy.orm import Session
from app.models.document import Document
from app.agents.unstructured_agent.ingestion import DocumentIngestionAgent
from backend.app.agents.unstructured_agent.chunking import ChunkingAgent
from app.agents.unstructured_agent.embedding import EmbeddingAgent

class DocumentService:

    def __init__(self):
        self.ingestion = DocumentIngestionAgent()
        self.chunker   = ChunkingAgent(chunk_size=500, overlap=50)
        self.embedder  = EmbeddingAgent()

    def process_document(self, doc_id: int, file_path: str, db: Session) -> dict:
        # Step 1: Extract text
        text = self.ingestion.extract(file_path)
        if not text:
            return {"success": False, "error": "Could not extract text"}

        # Step 2: Update document record with raw text
        doc          = db.query(Document).filter(Document.id == doc_id).first()
        if not doc:
            return {"success": False, "error": "Document not found"}

        doc.raw_text = text
        db.commit()

        # Step 3: Chunk the text
        chunks = self.chunker.chunk_with_metadata(text, doc_id)

        # Step 4: Embed and store in Pinecone
        count = self.embedder.upsert_chunks(chunks)

        # Step 5: Mark as indexed
        doc.is_indexed = 1
        doc.page_count = text.count("[Page ")
        # this page_count method ("[page") used for measure the page count of the document(after extract text)
        db.commit()

        return {
            "success":      True,
            "chunks_stored": count,
            "text_length":  len(text)
        }