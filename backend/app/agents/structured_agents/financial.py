# backend/app/agents/structured_agents/financial.py

import math
import pandas as pd
from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent
from difflib import get_close_matches


def safe_float(value, decimals: int = 2) -> Optional[float]:
    """Return rounded float, or None if value is nan/inf/None."""
    try:
        v = float(value)
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, decimals)
    except (TypeError, ValueError):
        return None


def safe_series_div(num: pd.Series, den: pd.Series) -> Optional[float]:
    """
    Divide two Series element-wise, replace zeros in denominator with NaN,
    take the mean, then sanitize. Never raises ambiguous truth-value error.
    """
    try:
        result = num / den.replace(0, float("nan"))
        return safe_float(result.mean())
    except Exception:
        return None


def safe_sum_div(num: pd.Series, den: pd.Series, scale: float = 100) -> Optional[float]:
    """sum(num) / sum(den) * scale — for ROA/ROE style calculations."""
    try:
        d = float(den.sum())
        if d == 0:
            return None
        return safe_float((float(num.sum()) / d) * scale)
    except Exception:
        return None


class FinancialAgent(BaseAgent):

    def __init__(self):
        super().__init__("FinancialAgent")

    def detect_language(self, text: str) -> str:
        if not text.strip():
            return "english"
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)
        return "sinhala" if sinhala_chars else "english"

    async def run(self, data: pd.DataFrame, context: Optional[str] = None) -> Dict:
        df         = data.copy()
        user_input = context or ""
        language   = self.detect_language(user_input)
        ratios: Dict[str, float] = {}

        # ── Column finder ─────────────────────────────────────────────
        def find_column(possible_names):
            cols_lower = {c.lower().replace(" ", "_"): c for c in df.columns}
            for key, original in cols_lower.items():
                for name in possible_names:
                    if name in key or key in name:
                        return pd.to_numeric(df[original], errors="coerce")
            for name in possible_names:
                matches = get_close_matches(name, cols_lower.keys(), n=1, cutoff=0.7)
                if matches:
                    return pd.to_numeric(df[cols_lower[matches[0]]], errors="coerce")
            return None

        # ── Locate columns ────────────────────────────────────────────
        curr_a    = find_column(["current_asset", "current_assets"])
        curr_l    = find_column(["current_liability", "current_liab"])
        inventory = find_column(["inventory", "inventories"])
        net_inc   = find_column(["net_income", "net_profit", "profit"])
        assets    = find_column(["total_asset", "total_assets", "asset"])
        debt      = find_column(["debt", "total_debt", "borrowings"])
        equity    = find_column(["equity", "stockholder", "shareholder_equity"])
        cogs      = find_column(["cost_of_goods", "cogs", "cost"])
        price     = find_column(["price", "share_price", "market_price"])
        eps       = find_column(["eps", "earnings_per_share"])

        # ── Calculate ratios — each block is fully independent ────────

        # Current Ratio
        if curr_a is not None and curr_l is not None:
            v = safe_series_div(curr_a, curr_l)
            if v is not None:
                ratios["current_ratio"] = v

        # Quick Ratio — compute quick_a as a Series BEFORE calling helper
        if curr_a is not None and inventory is not None and curr_l is not None:
            quick_a = curr_a - inventory          # Series - Series = Series (safe)
            v = safe_series_div(quick_a, curr_l)
            if v is not None:
                ratios["quick_ratio"] = v

        # Return on Assets
        if net_inc is not None and assets is not None:
            v = safe_sum_div(net_inc, assets)
            if v is not None:
                ratios["return_on_assets_pct"] = v

        # Return on Equity
        if net_inc is not None and equity is not None:
            v = safe_sum_div(net_inc, equity)
            if v is not None:
                ratios["return_on_equity_pct"] = v

        # Debt to Equity
        if debt is not None and equity is not None:
            v = safe_series_div(debt, equity)
            if v is not None:
                ratios["debt_to_equity"] = v

        # Inventory Turnover
        if cogs is not None and inventory is not None:
            v = safe_series_div(cogs, inventory)
            if v is not None:
                ratios["inventory_turnover"] = v

        # P/E Ratio
        if price is not None and eps is not None:
            v = safe_series_div(price, eps)
            if v is not None:
                ratios["pe_ratio"] = v

        # ── No ratios calculated ──────────────────────────────────────
        if not ratios:
            return self._format_result("FinancialAgent", {
                "language_detected": language,
                "ratios":            {},
                "assessment":        (
                    "Required financial columns (assets, equity, liabilities, etc.) "
                    "were not found in the dataset."
                )
            })

        # ── Grounded, length-controlled prompt ────────────────────────
        prompt = f"""You are a financial analyst.

Language to respond in: {language}

Calculated ratios from the uploaded data:
{ratios}

STRICT RULES:
- Interpret ONLY the ratios listed above. Do not mention or calculate others.
- One sentence per ratio explaining whether it looks healthy, average, or concerning.
- Flag any ratio that looks unusual (very high or very low) and explain why briefly.
- Do NOT add recommendations or action plans.
- Do NOT reference industry benchmarks unless you are certain they apply to this data.
- Maximum 150 words total."""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("FinancialAgent", {
            "language_detected": language,
            "ratios":            ratios,
            "assessment":        response.content
        })