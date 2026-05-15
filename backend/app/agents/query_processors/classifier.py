from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent

class ClassifierAgent(BaseAgent):

    def __init__(self):
        super().__init__("ClassifierAgent")

    async def classify(self, query: str) -> str:
        # NOTE: This only runs when system_route is None
        # (user asked a question without selecting any file)
        prompt = f"""You are a query router for a data analysis system.
Classify this query into EXACTLY ONE category:

- structured   → numbers, revenue, profit, KPIs, trends, calculations, Excel, CSV, data analysis
- unstructured → documents, PDFs, text content, summaries, contracts, policies, "what does it say"
- hybrid       → needs BOTH data analysis AND document content together

Query: "{query}"

Reply with ONLY one word: structured OR unstructured OR hybrid"""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        result   = response.content.strip().lower().split()[0]
        # .split()[0] takes first word only — prevents "structured data" causing KeyError

        valid = {"structured", "unstructured", "hybrid"}
        # ✅ FIX: fallback was "financial" which is NOT a valid graph route
        # Must be "structured" so graph can route to "trend" node
        return result if result in valid else "structured"

    async def run(self, data: Any, context: Optional[str] = None) -> Dict:
        query      = data if isinstance(data, str) else data.get("query", "")
        query_type = await self.classify(query)
        return self._format_result(self.name, {"query_type": query_type})