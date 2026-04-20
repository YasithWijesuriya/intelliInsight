# PURPOSE: Detects unusual values (outliers) in financial data
# Method: Z-score — values more than 2.5 standard deviations from mean
#         are flagged as anomalies
# Example: "Inventory spike in row 47: $450,000 vs average $12,000"

import pandas as pd
import numpy as np
from typing import Dict,Any
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent

class AnomalyAgent(BaseAgent):

    def __init__(self):
        super().__init__("AnomalyAgent")

    async def run(self, data: pd.DataFrame,context=None) -> Dict:
        df = data
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        anomalies    = {}

        for col in numeric_cols:
            series = df[col].dropna()
            if len(series) < 4:
                continue   # need enough data for meaningful stats

            mean    = series.mean()
            std     = series.std()

            if std == 0:
                continue   # all values same = no anomalies possible

            # Z-score formula: (value - mean) / std_deviation
            # If |z-score| > 2.5, it's an anomaly (top/bottom 1.2%)
            z_scores = (series-mean).abs() / std
            outlier_indices = z_scores[z_scores > 2.5].index.tolist()

            if outlier_indices:
                anomalies[col] = {
                    "anomalous_values": series[outlier_indices].tolist(),
                    "mean":  round(float(mean), 2),
                    "std":   round(float(std), 2),
                    "count": len(outlier_indices)
                }

        if not anomalies:
            return self._format_result("AnomalyAgent", {
                "message":   "No significant anomalies detected",
                "anomalies": {}
            })

        # Ask GPT-4 to explain what the anomalies mean
        prompt = f"""You are a financial auditor and risk analyst.
                        The following anomalies were detected using Z-score analysis (threshold: 2.5 std deviations).

                        Anomalies detected:
                        {anomalies}

                        For each anomaly:
                        1. Explain what this unusual value likely means in a business context
                        2. Assess the risk level (Low/Medium/High)
                        3. Recommend what action should be investigated
                        4. Could this be data entry error or a real business event?"""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("AnomalyAgent", {
            "anomalies":   anomalies,
            "explanation": response.content
        })