# PURPOSE: Generates strategic business recommendations
# This is the FINAL agent in the structured pipeline
# It receives results from all previous agents and synthesizes recommendations

from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent

class AdvisorAgent(BaseAgent):

    def __init__(self):
        super().__init__("AdvisorAgent")

    def detect_language(self, text: str) -> str:
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)

        if sinhala_chars:
            return "sinhala"
        return "english"

    async def run(self, data: Dict[str, Any],context:Optional[str]=None) -> Dict:
        # data contains results from ALL previous agents:
        # data["trend"]    = TrendAgent result
        # data["anomaly"]  = AnomalyAgent result
        # data["kpi"]      = KPIEngine result
        # data["financial"]= FinancialAgent result
        user_input = context or ""

        language = self.detect_language(user_input)

        trend_summary    = data.get("trend",    {}).get("result", {}).get("ai_analysis", "N/A")
        anomaly_summary  = data.get("anomaly",  {}).get("result", {}).get("explanation", "N/A")
        kpi_summary      = data.get("kpi",      {}).get("result", {}).get("interpretation", "N/A")
        financial_summary= data.get("financial",{}).get("result", {}).get("assessment", "N/A")
        
       
        prompt = f"""You are a Chief Financial Officer (CFO) and strategic business advisor.
                        You have received analysis from multiple AI agents. Synthesize all findings into
                        actionable strategic recommendations.

                        IMPORTANT RULES:
                            - Respond ONLY in {language}

                        TREND ANALYSIS:
                        {trend_summary}

                        ANOMALY DETECTION:
                        {anomaly_summary}

                        KPI ASSESSMENT:
                        {kpi_summary}

                        FINANCIAL RATIO ANALYSIS:
                        {financial_summary}

                        Based on ALL of the above, provide:
                        1. EXECUTIVE SUMMARY (3 sentences max — what leadership needs to know NOW)
                        2. TOP 5 PRIORITY ACTIONS (ordered by urgency, specific and actionable)
                        3. RISK ALERTS (anything requiring immediate attention)
                        4. 90-DAY ROADMAP (what to focus on in the next 3 months)
                        5. GROWTH OPPORTUNITIES (what is working well that should be doubled down on)

                        Format as a professional CFO briefing document."""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("AdvisorAgent", {
            "recommendations": response.content
        }, confidence=0.85)