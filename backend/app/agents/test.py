
from app.agents.base import BaseAgent
from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage

class TestAgent(BaseAgent):

    async def run(self, data: Any, context: Optional[str] = None) -> Dict:
        response = await self.llm.ainvoke([
            HumanMessage(content=data)
])

        return self._format_result(
            agent=self.name,
            result=response.content,
            confidence=1.0
        )