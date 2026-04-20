# PURPOSE: Parent class for ALL agents
# Every agent inherits from this so they all have:
# - A name
# - Access to the LLM (GPT-4)
# - A consistent result format

from abc import ABC, abstractmethod
# ABC = Abstract Base Class = you cannot create a BaseAgent directly
# abstractmethod = subclasses MUST implement this method

from typing import Any, Dict,Optional
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from config import settings

class BaseAgent(ABC):

    def __init__(self, name: str):
        self.name = name
        self.llm  = ChatOpenAI(
            model=settings.OPENAI_MODEL,         
            temperature=settings.OPENAI_TEMPERATURE,  
            api_key=SecretStr(settings.OPENAI_API_KEY.get_secret_value())
        )
        # self.llm is now your GPT-4 connection
        # Call it with: await self.llm.ainvoke([HumanMessage(content="...")])

    @abstractmethod
    async def run(self, data: Any,context:Optional[str]=None) -> Dict:
        # abstract = every subclass MUST have a run() method
        # async = runs asynchronously (non-blocking)
        pass

    def _format_result(self, agent: str, result: Any, confidence: float = 0.9) -> Dict:
        # Consistent output format for ALL agents
        return {
            "agent":      agent,
            "result":     result,
            "confidence": confidence
        }

