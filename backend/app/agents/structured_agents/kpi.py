# PURPOSE: Calculates Key Performance Indicators from financial data
# Automatically detects column names and calculates relevant ratios
# Example KPIs: Gross Margin %, Net Margin %, Current Ratio, ROE

from matplotlib import text
import pandas as pd
from typing import Dict,Optional,Any
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent
from difflib import get_close_matches


class KPIEngine(BaseAgent):

    def __init__(self):
        super().__init__("KPIEngine")

    def detect_language(self, text: str) -> str:
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)

        if sinhala_chars:
            return "sinhala"
        return "english"

    async def run(self, data: pd.DataFrame,context:Optional[str]=None) -> Dict: 
        df = data
        user_input = context or ""

        kpis = {}
        language = self.detect_language(user_input)

        
        def find_column(df, possible_names):
            cols = list(df.columns)

            cols_lower = {c.lower().replace(" ", "_"): c for c in cols} #This is called a #!dictionary comprehension
            #EX- "sales_revenue": "Sales Revenue" (output will be like this key:value)

        # 1. Exact / contains match
            for key, value in cols_lower.items():
                for name in possible_names:
                    if name in key or key in name:
                        return df[value]

            # 2. Fuzzy match (fallback)
            for name in possible_names:
                matches = get_close_matches(name, cols_lower.keys(), n=1, cutoff=0.7)
                if matches:
                    return df[cols_lower[matches[0]]]

            return None

        revenue = find_column(df, ["revenue", "sales", "income"])
        cost = find_column(df, ["cost", "cogs", "expense"])
        net_income = find_column(df, ["net_income", "net_profit", "profit"])
        assets = find_column(df, ["asset", "total_asset"])
        liab = find_column(df, ["liability", "debt"])
        equity = find_column(df, ["equity", "shareholder_equity"])
        curr_asset = find_column(df, ["current_asset", "short_term_asset"])
        curr_liab = find_column(df, ["current_liability", "short_term_liability"])

        if revenue is not None and cost is not None:
            gross_profit  = revenue - cost
            kpis["gross_margin_pct"] = round(
                float((gross_profit / revenue * 100).mean()), 2
            )

        if net_income is not None and revenue is not None:
            kpis["net_margin_pct"] = round(
                float((net_income / revenue * 100).mean()), 2
            )

        if curr_asset is not None and curr_liab is not None:
            kpis["current_ratio"] = round(
                float((curr_asset / curr_liab).mean()), 2
            )
            # Current ratio > 2.0 = healthy, < 1.0 = cash flow risk

        if net_income is not None and equity is not None:
            kpis["return_on_equity"] = round(
                float((net_income / equity * 100).mean()), 2    
                #this "2"value mean is to round the final output to 2 decimal places
            )

        # Ask GPT-4 to provide context and identify additional KPIs
        available_cols = df.columns.tolist()
        prompt = f""" You are a senior financial analyst and KPI specialist.

                            IMPORTANT RULES:
                            - Respond ONLY in {language}
                            - Do NOT invent data
                            - Use only given KPIs

                            Available columns:
                            {available_cols}

                            Calculated KPIs:
                            {kpis}

                            TASKS:

                            1. Interpret each KPI (good / bad / average)
                            2. Suggest additional KPIs
                            3. Give 3 key business insights
                            4. Flag risks or urgent issues

                            Be structured and concise.
                            """

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("KPIEngine", {
            "language_detected": language,
            "calculated_kpis":  kpis,
            "interpretation":   response.content,
            "columns_available": available_cols
        })