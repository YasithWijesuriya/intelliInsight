import pandas as pd
from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent
from difflib import get_close_matches

class FinancialAgent(BaseAgent):

    def __init__(self):
        super().__init__("FinancialAgent")
    
    def detect_language(self, text: str) -> str:
        if not text.strip():
            return "english"
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)
        return "sinhala" if sinhala_chars else "english"

    async def run(self, data: pd.DataFrame, context: Optional[str] = None) -> Dict:
        df = data.copy()
        user_input = context or ""
        ratios = {}
        language = self.detect_language(user_input)

        # 🔍 Column finder
        def find_column(df, possible_names):
            cols = list(df.columns)
            cols_lower = {c.lower().replace(" ", "_"): c for c in cols}

            # Direct match
            for key, value in cols_lower.items():
                for name in possible_names:
                    if name in key or key in name:
                        return pd.to_numeric(df[value], errors="coerce")

            # Fuzzy match
            for name in possible_names:
                matches = get_close_matches(name, cols_lower.keys(), n=1, cutoff=0.7)
                if matches:
                    return pd.to_numeric(df[cols_lower[matches[0]]], errors="coerce")

            return None

        #  Safe division
        def safe_div(numerator, denominator):
            return numerator / denominator.replace(0, pd.NA)

        curr_a = find_column(df, ["current_asset", "current_assets"])
        curr_l = find_column(df, ["current_liability", "current_liab"])

        inventory = find_column(df, ["inventory", "inventories"])
        net_inc = find_column(df, ["net_income", "net_profit", "profit"])
        revenue = find_column(df, ["revenue", "sales", "income"])
        assets = find_column(df, ["total_asset", "asset"])
        debt = find_column(df, ["debt", "total_debt", "borrowings"])
        equity = find_column(df, ["equity", "stockholder", "shareholder_equity"])
        cogs = find_column(df, ["cost_of_goods", "cogs", "cost"])
        price = find_column(df, ["price", "share_price", "market_price"])
        eps = find_column(df, ["eps", "earnings_per_share"])


        # Current Ratio
        if curr_a is not None and curr_l is not None:
            ratios["current_ratio"] = round(
                float(safe_div(curr_a, curr_l).mean()), 2
            )

        # Quick Ratio
        if curr_a is not None and inventory is not None and curr_l is not None:
            quick_a = curr_a - inventory
            ratios["quick_ratio"] = round(
                float(safe_div(quick_a, curr_l).mean()), 2
            )

        # ROA (correct method)
        if net_inc is not None and assets is not None:
            total_assets = assets.sum()
            if total_assets != 0:
                ratios["return_on_assets"] = round(
                    float((net_inc.sum() / total_assets) * 100), 2
                )

        # ROE
        if net_inc is not None and equity is not None:
            total_equity = equity.sum()
            if total_equity != 0:
                ratios["return_on_equity"] = round(
                    float((net_inc.sum() / total_equity) * 100), 2
                )

        # Debt to Equity
        if debt is not None and equity is not None:
            ratios["debt_to_equity"] = round(
                float(safe_div(debt, equity).mean()), 2
            )

        # Inventory Turnover
        if cogs is not None and inventory is not None:
            ratios["inventory_turnover"] = round(
                float(safe_div(cogs, inventory).mean()), 2
            )

        # P/E Ratio
        if price is not None and eps is not None:
            ratios["pe_ratio"] = round(
                float(safe_div(price, eps).mean()), 2
            )

        prompt = f"""
                You are a CFA (Chartered Financial Analyst).

                IMPORTANT RULES:
                - Respond ONLY in {language}
                - Use ONLY the ratios provided
                - Do NOT assume missing values
                - Do NOT generate new ratios

                Financial Ratios:
                {ratios}

                Provide:
                1. Overall financial health score (1-10) with justification
                2. Analysis of each ratio (with benchmark comparison)
                3. Key strengths
                4. Key risks
                5. Industry comparison (if possible)
                6. Recommendations
                """

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("FinancialAgent", {
            "language_detected": language,
            "ratios": ratios,
            "assessment": response.content
        })