from langgraph.graph import StateGraph, END
from typing import TypedDict, Optional, Any, Dict

from app.agents.query_processors.classifier import ClassifierAgent
from app.agents.structured_agents.trend import TrendAgent
from app.agents.structured_agents.anomaly import AnomalyAgent
from app.agents.structured_agents.kpi import KPIEngine
from app.agents.structured_agents.financial import FinancialAgent
from app.agents.structured_agents.advisor import AdvisorAgent
from app.agents.unstructured_agent.retrieval import RetrievalAgent
from app.agents.unstructured_agent.summary import SummaryAgent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.config import settings

# ── State ──────────────────────────────────────────────────────────
class AgentState(TypedDict):
    query:        str
    query_type:   Optional[str]
    df:           Optional[Any]
    document_id:  Optional[int]
    results:      Dict
    final_answer: Optional[str]
    error:        Optional[str]
    start_time:   Optional[float]
    system_route: Optional[str]


# ── Nodes ──────────────────────────────────────────────────────────

async def classify_node(state: AgentState) -> AgentState:
    # Only actually calls GPT when system_route is None
    # When system_route is set, this is a no-op pass-through
    if state.get("system_route") is not None:
        # System already decided — skip classifier entirely
        print(f"⏭️  classify_node skipped — system_route={state['system_route']}")
        return state

    classifier          = ClassifierAgent()
    query_type          = await classifier.classify(state["query"])
    state["query_type"] = query_type
    state["system_route"] = query_type   # sync so router sees it
    print(f"🤖 Classifier decided: {query_type}")
    return state


async def trend_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        state["results"]["trend"] = {"error": "No structured data loaded"}
        return state
    result = await TrendAgent().run(state["df"])
    state["results"]["trend"] = result
    return state


async def anomaly_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        return state
    result = await AnomalyAgent().run(state["df"])
    state["results"]["anomaly"] = result
    return state


async def kpi_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        return state
    result = await KPIEngine().run(state["df"])
    state["results"]["kpi"] = result
    return state


async def financial_node(state: AgentState) -> AgentState:
    if state["df"] is None:
        state["final_answer"] = "No structured data provided."
        return state
    result = await FinancialAgent().run(state["df"])
    state["results"]["financial"] = result
    return state


async def advisor_node(state: AgentState) -> AgentState:
    result = await AdvisorAgent().run(state["results"])
    state["results"]["advisory"] = result
    state["final_answer"]        = result["result"]["recommendations"]
    return state


async def retrieval_node(state: AgentState) -> AgentState:
    if not state.get("document_id"):
        state["results"]["retrieved_chunks"] = []
        state["final_answer"] = "No document selected. Please select a document first."
        return state

    # ✅ FIX: parameter is doc_id (not document_id)
    # RetrievalAgent.retrieve() signature: retrieve(query, top_k, doc_id)
    chunks = RetrievalAgent().retrieve(
        state["query"], top_k=5, doc_id=state["document_id"]
    )
    state["results"]["retrieved_chunks"] = chunks
    return state


async def summary_node(state: AgentState) -> AgentState:
    result = await SummaryAgent().run({
        "query":  state["query"],
        "chunks": state["results"].get("retrieved_chunks", [])
    })
    state["results"]["summary"] = result
    state["final_answer"]       = result["result"]["answer"]
    return state


async def hybrid_advisor_node(state: AgentState) -> AgentState:
 
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        temperature=0.1,          
        api_key=settings.OPENAI_API_KEY.get_secret_value()  # type: ignore
    )
 
    # Pull what each pipeline actually produced
    financial_answer = (
        state["results"]
        .get("advisory", {})
        .get("result", {})
        .get("recommendations", "")
        .strip()
    )

                        #     state = {
                        #     "results": {
                        #         "advisory": {
                        #             "result": {
                        #                 "recommendations":
                        #                 "Revenue dropped by 10%"
                        #             }
                        #         }
                        #     }
                        # }
    doc_answer = (
        state["results"]
        .get("summary", {})
        .get("result", {})
        .get("answer", "")
        .strip()
    )
 
    failure_phrases = [
    "insufficient information",
    "no relevant information",
    "unable to answer",
    "not enough information",
    "data not available"
]

    no_financial = (
        not financial_answer or
        any(p in financial_answer.lower() for p in failure_phrases)
    )

    no_doc = (
        not doc_answer or
        any(p in doc_answer.lower() for p in failure_phrases)
    )
 
    if no_financial and no_doc:
        state["final_answer"] = (
            "Neither the structured data nor the documents contained enough "
            "information to answer that question."
        )
        state["results"]["hybrid_synthesis"] = state["final_answer"]
        return state
 
    if no_financial:
        state["final_answer"] = doc_answer
        state["results"]["hybrid_synthesis"] = doc_answer
        return state
 
    if no_doc:
        state["final_answer"] = financial_answer
        state["results"]["hybrid_synthesis"] = financial_answer
        return state
 
    # Both sides have real content — combine them concisely
    system_msg = SystemMessage(content="""You are a concise analyst.
Your job is to merge two answers into ONE clear, unified response.
 
STRICT RULES:
1. Use ONLY the information from the two answers provided. Do not add outside knowledge.
2. Do not repeat the same point twice.
3. Keep the final answer under 200 words.
4. If the two answers contradict each other, say so clearly — do not smooth it over.
5. Never invent numbers, names, or conclusions not present in the inputs.
6. Do not add a preamble like "Based on both sources..." — go straight to the answer.""")
 
    user_msg = HumanMessage(content=f"""DATA ANALYSIS ANSWER:
{financial_answer}
 
DOCUMENT ANSWER:
{doc_answer}
 
USER QUESTION: {state["query"]}
 
Merge these two answers into one concise response. Clearly label insights that come from
the data vs the document only when it adds clarity.""")
 
    response = await llm.ainvoke([system_msg, user_msg])
 
    state["results"]["hybrid_synthesis"] = response.content
    state["final_answer"] = response.content  # type: ignore
    return state

# ── Router ─────────────────────────────────────────────────────────
def route_after_classify(state: AgentState) -> str:
    system_route = state.get("system_route")

    print(f"🔀 Router: system_route={system_route}")

    if system_route == "structured":
        return "trend"
    if system_route == "unstructured":
        return "retrieval"
    if system_route == "hybrid":
        return "hybrid_start"   # ✅ NEW hybrid entry point

    # Absolute fallback — should rarely reach here
    if state.get("df") is not None:
        return "trend"
    if state.get("document_id"):
        return "retrieval"
    return "trend"


# ── Graph ──────────────────────────────────────────────────────────
def build_agent_graph():
    graph = StateGraph(AgentState)

    # Register all nodes
    graph.add_node("classify",       classify_node)
    graph.add_node("trend",          trend_node)
    graph.add_node("anomaly",        anomaly_node)
    graph.add_node("kpi",            kpi_node)
    graph.add_node("financial",      financial_node)
    graph.add_node("advisor",        advisor_node)
    graph.add_node("retrieval",      retrieval_node)
    graph.add_node("summary",        summary_node)
    # ✅ NEW: hybrid nodes
    graph.add_node("hybrid_trend",         trend_node)
    graph.add_node("hybrid_anomaly",       anomaly_node)
    graph.add_node("hybrid_kpi",           kpi_node)
    graph.add_node("hybrid_financial",     financial_node)
    graph.add_node("hybrid_advisor",       advisor_node)
    graph.add_node("hybrid_retrieval",     retrieval_node)
    graph.add_node("hybrid_summary",       summary_node)
    graph.add_node("hybrid_final",         hybrid_advisor_node)

    graph.set_entry_point("classify")

    # Routing after classify
    graph.add_conditional_edges(
        "classify",
        route_after_classify,
        {
            "trend":        "trend",
            "retrieval":    "retrieval",
            "hybrid_start": "hybrid_trend",   # ✅ hybrid starts financial first
        }
    )

    # ── Structured pipeline ────────────────────────────────────────
    graph.add_edge("trend",     "anomaly")
    graph.add_edge("anomaly",   "kpi")
    graph.add_edge("kpi",       "financial")
    graph.add_edge("financial", "advisor")
    graph.add_edge("advisor",   END)

    # ── Unstructured pipeline ──────────────────────────────────────
    graph.add_edge("retrieval", "summary")
    graph.add_edge("summary",   END)

    # ── Hybrid pipeline: runs BOTH then combines ───────────────────
    graph.add_edge("hybrid_trend",     "hybrid_anomaly")
    graph.add_edge("hybrid_anomaly",   "hybrid_kpi")
    graph.add_edge("hybrid_kpi",       "hybrid_financial")
    graph.add_edge("hybrid_financial", "hybrid_advisor")
    graph.add_edge("hybrid_advisor",   "hybrid_retrieval")   # then RAG
    graph.add_edge("hybrid_retrieval", "hybrid_summary")
    graph.add_edge("hybrid_summary",   "hybrid_final")       # combine both
    graph.add_edge("hybrid_final",     END)

    return graph.compile()


agent_graph = build_agent_graph()