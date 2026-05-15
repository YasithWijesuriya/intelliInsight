# PURPOSE: Generates strategic recommendations from structured data analysis results
# IMPROVEMENTS:
#   - Shorter, tighter prompt — no "CFO briefing document" roleplay that inflates output
#   - Hard limits on output sections and length
#   - Instructs the model to omit sections it has no real evidence for
#   - Prevents hallucinated benchmarks and industry comparisons

# backend/app/agents/structured_agents/advisor.py

from typing import Dict, Any,Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent


class AdvisorAgent(BaseAgent):

    def __init__(self):
        super().__init__("AdvisorAgent")

    async def run(self, data: Dict[str, Any],context:Optional[str]=None) -> Dict:
        trend_result    = data.get("trend",    {}).get("result", {})
        anomaly_result  = data.get("anomaly",  {}).get("result", {})
        kpi_result      = data.get("kpi",      {}).get("result", {})
        financial_result= data.get("financial",{}).get("result", {})

        trend_summary    = trend_result.get("ai_analysis",    "").strip()
        anomaly_summary  = anomaly_result.get("explanation",  "").strip()
        kpi_summary      = kpi_result.get("interpretation",   "").strip()
        financial_summary= financial_result.get("assessment", "").strip()

        # Detect schema from KPI result for context
        schema = kpi_result.get("schema_detected", "unknown")
        kpis   = kpi_result.get("calculated_kpis", {})

        # Build only sections that have real content
        sections = []
        if trend_summary:
            sections.append(f"TREND ANALYSIS:\n{trend_summary}")
        if anomaly_summary:
            sections.append(f"ANOMALY DETECTION:\n{anomaly_summary}")
        if kpi_summary:
            sections.append(f"KPI INTERPRETATION:\n{kpi_summary}")
        if financial_summary:
            sections.append(f"FINANCIAL RATIOS:\n{financial_summary}")

        if not sections:
            return self._format_result("AdvisorAgent", {
                "recommendations": "Insufficient analysis data to generate recommendations."
            }, confidence=0.3)

        analysis_block = "\n\n".join(sections)

        schema_note = (
            "Note: The data is a transaction log (not a balance sheet). "
            "Interpret findings accordingly — revenue and costs are per-transaction."
            if schema == "transaction_log"
            else ""
        )

        prompt = f"""You are a business analyst reviewing findings from multiple analysis agents.

{schema_note}

Analysis findings:
{analysis_block}

Raw KPIs calculated: {kpis}

STRICT RULES:
- Base your response ONLY on the findings and KPIs above.
- Do NOT invent numbers, benchmarks, or trends not present above.
- Keep total response under 200 words.
- Use this structure (skip any section you have no real evidence for):

**Key Findings** (2–3 bullets — only what the data clearly shows)

**Priority Actions** (2–3 specific actions directly supported by the findings)

**Risks** (only if anomalies or negative trends were actually detected)"""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("AdvisorAgent", {
            "recommendations": response.content
        }, confidence=0.85)