# PURPOSE: Answers user questions using retrieved document chunks
# This is the final step in the RAG pipeline
# It takes relevant chunks + question → feeds to GPT-4 → returns answer

from typing import Dict, Optional
from app.agents.base import BaseAgent

class SummaryAgent(BaseAgent):

    def __init__(self):
        super().__init__("SummaryAgent")

    # Detect Sinhala or English
    def detect_language(self, text: str) -> str:
        if not text.strip():
            return "english"
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)
        return "sinhala" if sinhala_chars else "english"

    async def run(self, data: Dict, context: Optional[str] = None) -> Dict:
        query = data.get("query", "")
        chunks = data.get("chunks", [])
        user_input = context or ""

        language = self.detect_language(user_input)

        # Convert language to readable instruction
        language_instruction = (
            "Respond ONLY in Sinhala"
            if language == "sinhala"
            else "Respond ONLY in English"
        )

        # If no chunks found
        if not chunks:
            return self._format_result(
                "SummaryAgent",
                {
                    "answer": "No relevant information found in the documents.",
                    "sources": []
                },
                confidence=0.0
            )

        # Combine chunks into readable context
        context_text = "\n\n---\n\n".join(
            f"[Chunk {i+1} (relevance: {c['score']})]\n{c['text']}"
            for i, c in enumerate(chunks)
        )

        # FINAL PROMPT
        prompt = f"""
                    You are an intelligent document assistant.

                    IMPORTANT RULES:
                    - {language_instruction}
                    - Answer ONLY using the provided document context
                    - Do NOT add external knowledge
                    - If the answer is not in the context, say: "This information is not in the provided documents"
                    - Always mention which chunk the answer comes from

                    DOCUMENT CONTEXT:
                    {context_text}

                    USER QUESTION:
                    {query}

                    Provide a clear and accurate answer.
                    """

        # Call LLM
        response = await self.llm.ainvoke(prompt)

        # Return formatted result
        return self._format_result(
            "SummaryAgent",
            {
                "answer": response.content,
                "chunks_used": len(chunks),
                "top_relevance": chunks[0]["score"],
                "sources": [
                    {"doc_id": c.get("doc_id"), "score": c.get("score")}
                    for c in chunks
                ]
            }
        )