# PURPOSE: The master orchestrator — connects all agents using LangGraph
# LangGraph StateGraph = a directed graph where:
#   - Nodes = agents (functions that process state)
#   - Edges = connections between agents
#   - State = shared data dict passed between all agents

from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Any, Dict
import time

from app.agents.query_processors.classifier import ClassifierAgent
from app.agents.structured_agents.ingestion import StructuredIngestionAgent
from app.agents.structured_agents.trend import TrendAgent
from app.agents.structured_agents.anomaly import AnomalyAgent
from app.agents.structured_agents.kpi import KPIEngine
from app.agents.structured_agents.financial import FinancialAgent
from app.agents.structured_agents.advisor import AdvisorAgent
from app.agents.unstructured_agent.retrieval import RetrievalAgent
from app.agents.unstructured_agent.summary import SummaryAgent

# ── Shared State ───────────────────────────────────────────────────
# This dict is passed between EVERY agent in the graph
# Each agent can READ from it and WRITE to it
class AgentState(TypedDict):
    query:        str              # original user question
    query_type:   Optional[str]   # classified type
    df:           Optional[Any]   # pandas DataFrame (for financial)
    doc_id:       Optional[int]   # document ID (for RAG)
    results:      Dict            # each agent writes results here
    final_answer: Optional[str]   # the final response to the user
    error:        Optional[str]   # error message if something fails
    start_time:   Optional[float] # for timing

# ── Node Functions ─────────────────────────────────────────────────
# Each function = one node in the graph
# Must take AgentState and return AgentState

async def classify_node(state: AgentState) -> AgentState:
    classifier         = ClassifierAgent()
    query_type         = await classifier.classify(state["query"])
    state["query_type"] = query_type
    print(f"Query classified as: {query_type}")
    return state

async def trend_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        return state
    agent              = TrendAgent()
    result             = await agent.run(state["df"])
    state["results"]["trend"] = result
    return state

async def anomaly_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        return state
    agent              = AnomalyAgent()
    result             = await agent.run(state["df"])
    state["results"]["anomaly"] = result
    return state

async def kpi_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        return state
    agent              = KPIEngine()
    result             = await agent.run(state["df"])
    state["results"]["kpi"] = result
    return state

async def financial_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        return state
    agent              = FinancialAgent()
    result             = await agent.run(state["df"])
    state["results"]["financial"] = result
    return state

async def advisor_node(state: AgentState) -> AgentState:
    agent              = AdvisorAgent()
    result             = await agent.run(state["results"])
    state["results"]["advisory"]  = result
    state["final_answer"]         = result["result"]["recommendations"]
    return state

async def retrieval_node(state: AgentState) -> AgentState:
    agent  = RetrievalAgent()
    chunks = agent.retrieve(state["query"], top_k=5, doc_id=state.get("doc_id"))
    state["results"]["retrieved_chunks"] = chunks
    return state

async def summary_node(state: AgentState) -> AgentState:
    agent  = SummaryAgent()
    result = await agent.run({
        "query":  state["query"],
        "chunks": state["results"].get("retrieved_chunks", [])
    })
    state["results"]["summary"] = result
    state["final_answer"]       = result["result"]["answer"]
    return state

# ── Routing Function ───────────────────────────────────────────────
def route_after_classify(state: AgentState) -> str:
    # This function decides which node to go to after classification
    qtype = state.get("query_type", "financial")
    if qtype == "document":
        return "retrieval"    # go to RAG pipeline
    if qtype == "hybrid":
        return "trend"        # run financial first, then docs
    return "trend"            # default: financial pipeline

# ── Build the Graph ────────────────────────────────────────────────
def build_agent_graph():
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("classify",  classify_node)
    graph.add_node("trend",     trend_node)
    graph.add_node("anomaly",   anomaly_node)
    graph.add_node("kpi",       kpi_node)
    graph.add_node("financial", financial_node)
    graph.add_node("advisor",   advisor_node)
    graph.add_node("retrieval", retrieval_node)
    graph.add_node("summary",   summary_node)

    # Set entry point
    graph.set_entry_point("classify")

    # After classify: route based on query type
    graph.add_conditional_edges(
        "classify",         # from this node
        route_after_classify,   # call this function to decide where to go
        {
            "trend":    "trend",       # if returns "trend" → go to trend node
            "retrieval":"retrieval",   # if returns "retrieval" → go to retrieval
        }
    )

    # Financial pipeline: trend → anomaly → kpi → financial → advisor → END
    graph.add_edge("trend",     "anomaly")
    graph.add_edge("anomaly",   "kpi")
    graph.add_edge("kpi",       "financial")
    graph.add_edge("financial", "advisor")
    graph.add_edge("advisor",   END)

    # Document pipeline: retrieval → summary → END
    graph.add_edge("retrieval", "summary")
    graph.add_edge("summary",   END)

    return graph.compile()

# Create ONE compiled graph instance (reused for all requests)
agent_graph = build_agent_graph()