# PURPOSE: Detects trends in numerical data
# Uses Pandas to calculate statistics, then GPT-4 to explain them
# Example output: "Revenue grew 15% MoM, operating costs spiked in Q3"

import pandas as pd
from typing import Dict
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent

class TrendAgent(BaseAgent):

    def __init__(self):
        super().__init__("TrendAgent")

    async def run(self, data: pd.DataFrame,context=None) -> Dict:
        df = data
        # Step 1: Find all numeric columns
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        if not numeric_cols:
            return self._format_result("TrendAgent",
                {"error": "No numeric columns found in data"})

        # Step 2: Calculate statistics for each numeric column
        stats = {}
        for col in numeric_cols[:6]:   # max 6 columns to save tokens
            series = df[col].dropna()  # remove empty cells

            if len(series) < 2:
                continue

            stats[col] = {
                "min":          float(series.min()),
                "max":          float(series.max()),
                "mean":         float(series.mean()),
                "std":          float(series.std()),
                "first_value":  float(series.iloc[0]),   # iloc[0] = first row
                "last_value":   float(series.iloc[-1]),  # iloc[-1] = last row
                "total_change": float(series.iloc[-1] - series.iloc[0]),
                "pct_change":   float(
                    (series.iloc[-1] - series.iloc[0]) / series.iloc[0] * 100
                ) if series.iloc[0] != 0 else 0.0
                # pct_change = percentage change from first to last value
            }

        # Step 3: Send stats to GPT-4 for human-readable analysis
        prompt = f"""You are a senior financial analyst.
                    Analyse these statistics from a business dataset and identify key trends.

                    Column Statistics:
                    {stats}

                    Provide:
                    1. Top 3 most important trends you can see
                    2. Which metrics are growing vs declining
                    3. Any concerning patterns
                    4. Month-over-month or period-over-period movements

                    Be specific with numbers. Format as clear bullet points."""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        # ainvoke = async invoke = sends message to GPT-4 and waits for reply

        return self._format_result("TrendAgent", {
            "statistics":  stats,
            "ai_analysis": response.content
            # response.content = the text GPT-4 wrote back
        })