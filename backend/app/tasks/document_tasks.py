
from app.database import SessionLocal
from app.services.document_service import DocumentService

def process_doc_task(doc_id: int, file_path: str):
    db = SessionLocal()
    try:
        service = DocumentService()
        service.process_document(doc_id, file_path, db)
    except Exception as e:
        print(f"❌ Background task failed for doc {doc_id}: {e}")
        # Mark as error in DB
        from app.models.document import Document
        doc = db.query(Document).filter(Document.id == doc_id).first()
        if doc:
            doc.is_indexed = 2
            db.commit()
    finally:
        db.close()