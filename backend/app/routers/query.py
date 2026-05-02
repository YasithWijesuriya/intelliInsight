# PURPOSE: The main /query endpoint that users call to ask questions
# This router receives the query, runs the agent graph, returns the answer

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import time, pandas as pd

from database import get_db
from app.schemas.query import QueryRequest, QueryResponse
from app.models.query import Query
from app.models.data_source import DataSource
from app.agents.orchestrator import agent_graph, AgentState
from app.agents.structured_agents.ingestion import StructuredIngestionAgent

router = APIRouter(prefix="/query", tags=["Query"])

@router.post("/")
async def process_query(request: QueryRequest, db: Session = Depends(get_db)):
    start = time.time()

    # Step 1: If a data source ID was given, load the file
    df = None
    if request.data_source_id:
        source = db.query(DataSource).filter(
            DataSource.id == request.data_source_id
        ).first()
        #db.query(Data_source) = “SELECT * FROM DataSource”
        # .first() = “LIMIT 1” — Give me the first row only from the result

        if not source:
            raise HTTPException(404, "Data source not found")

        loader = StructuredIngestionAgent()
        df     = loader.load_file(str(source.file_path))
        # df is now a pandas DataFrame ready for agents

    # Step 2: Build initial state for the graph
    initial_state: AgentState = {
        "query":        request.query,
        "query_type":   None,
        "df":           df,
        "doc_id":       request.document_id,
        "results":      {},
        "final_answer": None,
        "error":        None,
        "start_time":   start
    }

    # Step 3: Run the agent graph (this is where all the AI happens!)
    final_state = await agent_graph.ainvoke(initial_state)

    exec_time = int((time.time() - start) * 1000)  # milliseconds

    # Step 4: Save query + result to database
    query_record = Query(
        user_query   = request.query,
        query_type   = final_state.get("query_type"),
        response     = final_state.get("final_answer"),
        sources_used = ",".join(final_state["results"].keys()),
        confidence   = 0.9,
        exec_time_ms = exec_time
    )
    db.add(query_record)
    db.commit()
    db.refresh(query_record)

    # Step 5: Return response to the frontend
    return {
        "id":           query_record.id,
        "query":        request.query,
        "query_type":   final_state.get("query_type"),
        "answer":       final_state.get("final_answer"),
        "results":      final_state["results"],
        "exec_time_ms": exec_time
    }