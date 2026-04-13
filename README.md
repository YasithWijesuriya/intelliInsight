backend/app/
├── agents/
│ ├── cross_source_agents/
│ │ ├── recommendation.py
│ │ ├── response_generator.py
│ │ └── validation.py
│ ├── inventory_agents/
│ │ ├── alert_generator.py
│ │ ├── detector.py
│ │ ├── parser.py
│ │ └── whatsapp_sender.py
│ ├── query_processors/
│ │ ├── analyzer.py
│ │ ├── classifier.py
│ │ └── supervisor.py
│ ├── structured_agents/
│ │ ├── advisor.py
│ │ ├── anomaly.py
│ │ ├── financial.py
│ │ ├── ingestion.py
│ │ ├── kpi.py
│ │ └── trend.py
│ ├── unstructured_agent/
│ │ ├── chunking.py
│ │ ├── email.py
│ │ ├── embedding.py
│ │ ├── ingestion.py
│ │ ├── ocr.py
│ │ ├── retrieval.py
│ │ ├── summary.py
│ │ └── synthesis.py
│ ├── base.py
│ └── orchestrator.py
├── models/
│ ├── **init**.py
│ ├── analysis.py
│ ├── data_source.py
│ ├── document.py
│ ├── product_stock.py
│ ├── query.py
│ ├── structured_data.py
│ ├── unstructured_data.py
│ ├── user.py
│ └── vector_index.py
├── routers/
│ ├── auth.py
│ ├── documents.py
│ ├── query.py
│ ├── stock.py
│ ├── structural_analysis.py
│ ├── upload.py
│ ├── webhook.py
│ └── websocket.py
├── schemas/
│ ├── **init**.py
│ ├── analysis.py
│ ├── data_source.py
│ ├── document.py
│ ├── query.py
│ ├── stock.py
│ └── user.py
├── services/
│ ├── document_service.py
│ ├── file_service.py
│ ├── notification_service.py
│ ├── stock_service.py
│ ├── structured_data_service.py
│ └── vector_service.py
├── uploads/
│ ├── stock/
│ ├── structured/
│ └── unstructured/
└── utils/
├── **init**.py
├── config.py
├── database.py
└── main.py



this function need  to us for  auto delete unusable files from database 

exmple only : - 

@app.post("/ask")
def ask_question(data: QuestionRequest, db: Session):

    document = db.query(Document).filter(Document.id == data.document_id).first()

    if not document:
        return {"error": "Document not found"}

    # 🔥 THIS IS WHAT YOU ADD
    document.last_accessed = datetime.utcnow()
    db.commit()

    # continue AI pipeline
    answer = process_rag(data.question, document.id)

    return {"answer": answer}



So where exactly in your project?
Your project likely has (or should have):

app/
 ├── main.py ❌ (not here)
 ├── routes/
 │     ├── document.py ✅ (here)
 │     ├── rag.py ✅ (or here)
 ├── services/
 │     ├── rag_service.py ✅ (or here)