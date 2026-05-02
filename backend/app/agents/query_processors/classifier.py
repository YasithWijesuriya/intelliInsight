from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent

class ClassifierAgent(BaseAgent):

    def __init__(self):
        super().__init__("ClassifierAgent")

    async def classify(self, query: str) -> str:
        prompt = f"""Classify this user query into EXACTLY ONE of these categories:
- financial: questions about numbers, revenue, costs, KPIs, trends, ratios
- document: questions about document content, contracts, reports, policies
- advisory: questions asking for recommendations, what should we do, strategy
- comparative: questions comparing two things, vs, difference between
- hybrid: questions that need BOTH financial data AND documents

Query: "{query}"

Respond with ONLY the category word (e.g., "financial"). No explanation."""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        result   = response.content.strip().lower()

        valid = {"financial", "document", "advisory", "comparative", "hybrid"}
        return result if result in valid else "financial"

    async def run(self, data: Any, context: Optional[str] = None) -> Dict:
        query = data if isinstance(data, str) else data.get("query")

        query_type = await self.classify(query)

        return self._format_result(
            agent=self.name,
            result={"query_type": query_type}
        )