
# PURPOSE: Answers user questions using retrieved document chunks
# IMPROVEMENTS:
#   - Strict instruction to never go beyond what the chunks contain
#   - Hard word limit to prevent bloated answers
#   - Explicit fallback when chunks don't answer the question
#   - No speculative or background "context" additions

from typing import List, Dict,Optional
from langchain_core.messages import HumanMessage, SystemMessage
from app.agents.base import BaseAgent


class SummaryAgent(BaseAgent):

    def __init__(self):
        super().__init__("SummaryAgent")

    def detect_language(self, text: str) -> str:
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)

        if sinhala_chars:
            return "sinhala"
        return "english"

    async def run(self, data: Dict,context:Optional[str]=None) -> Dict:
        query  = data.get("query", "")
        chunks = data.get("chunks", [])
        user_input = context or ""
        language = self.detect_language(user_input)

        print(f"[DEBUG SummaryAgent] query='{query}' | chunks received={len(chunks)}")

        if chunks:
            print(f"[DEBUG SummaryAgent] first chunk preview: {chunks[0]}")

        if not chunks:
            return self._format_result("SummaryAgent", {
                "answer":  "No relevant information was found in the uploaded documents for that question.",
                "sources": []
            }, confidence=0.0)

        # Only use top-3 most relevant chunks to avoid noise
        top_chunks = sorted(chunks, key=lambda c: c.get("score", 0), reverse=True)[:3]

        context_text = "\n\n---\n\n".join(
            f"[Chunk {i+1} | relevance: {c['score']}]\n{c['text']}"
            for i, c in enumerate(top_chunks)
        )

        system_msg = SystemMessage(content="""You are a precise document assistant.

STRICT RULES — follow every one without exception:
1. Answer ONLY from the document chunks provided. Do not add background knowledge.
2. If the chunks do not contain enough information to answer, say exactly:
   "The documents don't contain enough information to answer this question."
3. Be concise. Maximum 150 words unless the question explicitly asks for a list or table.
4. Never pad the answer with phrases like "Based on the provided context..." or "In conclusion...".
5. Never speculate or infer beyond what is explicitly stated in the chunks.
6. If quoting, keep quotes under 20 words.""")

        user_msg = HumanMessage(content=f"""DOCUMENT CHUNKS:
{context_text}

QUESTION: {query}

Answer concisely and only from the chunks above.""")

        response = await self.llm.ainvoke([system_msg, user_msg])

        return self._format_result("SummaryAgent", {
            "answer":        response.content,
            "chunks_used":   len(top_chunks),
            "top_relevance": top_chunks[0]["score"] if top_chunks else 0,
            "sources":       [
                {"doc_id": c.get("document_id"), "score": c["score"]}
                for c in top_chunks
            ]
        })