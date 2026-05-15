from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time

from app.database import get_db
from app.schemas.query import QueryRequest
from app.models.query import Query
from app.models.data_source import DataSource
from app.models.document import Document
from app.agents.orchestrator import agent_graph, AgentState
from app.agents.structured_agents.ingestion import StructuredIngestionAgent
from app.utils.sanitize import sanitize

router = APIRouter(prefix="/query", tags=["Query"])


@router.post("/")
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    start        = time.time()
    df           = None
    doc_id       = None
    system_route = None

    has_structured = request.data_source_id is not None
    has_document   = request.document_id is not None

    # ── Case 1: HYBRID — user selected BOTH a file AND a document ──
    if has_structured and has_document:
        # Load structured file
        source = db.query(DataSource).filter(
            DataSource.id == request.data_source_id
        ).first()
        if not source:
            raise HTTPException(404, f"Data source {request.data_source_id} not found")

        loader = StructuredIngestionAgent()
        df     = loader.load_file(str(source.file_path))
        if df is None:
            raise HTTPException(400, f"Could not read file: {source.file_path}")

        # Validate document
        doc = db.query(Document).filter(
            Document.id == request.document_id
        ).first()
        if not doc:
            raise HTTPException(404, f"Document {request.document_id} not found")
        if doc.is_indexed == 0:
            raise HTTPException(400, "Document is still processing. Please wait.")

        doc_id       = request.document_id
        system_route = "hybrid"
        print(f"🔀 System route: HYBRID | file={source.name} | doc={doc.filename}")

    # ── Case 2: STRUCTURED only ────────────────────────────────────
    elif has_structured:
        source = db.query(DataSource).filter(
            DataSource.id == request.data_source_id
        ).first()
        if not source:
            raise HTTPException(404, f"Data source {request.data_source_id} not found")

        loader = StructuredIngestionAgent()
        df     = loader.load_file(str(source.file_path))
        if df is None:
            raise HTTPException(400, f"Could not read file: {source.file_path}")

        system_route = "structured"
        print(f"📊 System route: STRUCTURED | file={source.name} | rows={len(df)}")

    # ── Case 3: UNSTRUCTURED only ──────────────────────────────────
    elif has_document:
        doc = db.query(Document).filter(
            Document.id == request.document_id
        ).first()
        if not doc:
            raise HTTPException(404, f"Document {request.document_id} not found")
        if doc.is_indexed == 0:
            raise HTTPException(
                400,
                f"Document '{doc.filename}' is still being processed. "
                "Please wait a moment and try again."
            )
        if doc.is_indexed == 2:
            raise HTTPException(
                400,
                f"Document '{doc.filename}' failed to process. "
                "Please re-upload the file."
            )

        doc_id       = request.document_id
        system_route = "unstructured"
        print(f"📄 System route: UNSTRUCTURED | doc={doc.filename}")

    # ── Case 4: No file selected — classifier decides ──────────────
    else:
        system_route = None
        print("⚠️  No file selected — classifier will decide")

    # ── Build state ────────────────────────────────────────────────
    initial_state: AgentState = {
        "query":        request.query,
        "query_type":   None,
        "df":           df,
        "document_id":  doc_id,
        "results":      {},
        "final_answer": None,
        "error":        None,
        "start_time":   start,
        "system_route": system_route,   # type: ignore
    }

    # ── Run agent graph ────────────────────────────────────────────
    try:
        final_state = await agent_graph.ainvoke(initial_state)
    except Exception as e:
        print("❌ AGENT GRAPH ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    exec_time   = int((time.time() - start) * 1000)
    ROUTE_TO_QUERY_TYPE = {
    "structured":   "financial",    # structured file → financial query type
    "unstructured": "document",     # document file   → document query type  
    "hybrid":       "hybrid",       # both            → hybrid query type
    None:           None
}


    clean_results = sanitize(final_state["results"])  
    final_answer  = final_state.get("final_answer") or ""

    # ── Save to DB ─────────────────────────────────────────────────
    query_record = Query(
        user_query   = request.query,
        query_type   = ROUTE_TO_QUERY_TYPE.get(system_route),
        response     = final_answer,
        sources_used = ",".join(final_state["results"].keys()),
        confidence   = 0.9,
        exec_time_ms = exec_time
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    return {
        "id":           query_record.id,
        "query":        request.query,
        "route_used":   system_route,
        "query_type":   final_state.get("query_type") or system_route,
        "answer":       final_answer,
        "results":      clean_results,
        "exec_time_ms": exec_time
    }