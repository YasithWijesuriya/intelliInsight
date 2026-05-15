# PURPOSE: Calculates Key Performance Indicators from financial data
# IMPROVEMENTS:
#   - Removes "suggest additional KPIs" instruction that causes hallucination
#   - Instructs model to skip interpretation for KPIs it didn't calculate
#   - Hard word limit
#   - Explicit instruction: do not invent numbers
import math
import pandas as pd
from typing import Dict, Optional, Any
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent
from app.utils.schema_detector import detect_schema,get_schema_summary
from difflib import get_close_matches

def safe_float(value, decimals: int = 2) -> Optional[float]:
    try:
        v = float(value)
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, decimals)
    except (TypeError, ValueError):
        return None

class KPIEngine(BaseAgent):

    def __init__(self):
        super().__init__("KPIEngine")

    def detect_language(self, text: str) -> str:
        sinhala_chars = any('\u0D80' <= c <= '\u0DFF' for c in text)
        return "sinhala" if sinhala_chars else "english"
    
    def find_column(self, df: pd.DataFrame, possible_names):
        cols_lower = {c.lower().replace(" ", "_"): c for c in df.columns}#This is called a #!dictionary comprehension
            #EX- "sales_revenue": "Sales Revenue" (output will be like this key:value)
        for key, original in cols_lower.items():
            for name in possible_names:
                if name in key or key in name:
                    return pd.to_numeric(df[original], errors="coerce")
        for name in possible_names:
            matches = get_close_matches(name, cols_lower.keys(), n=1, cutoff=0.7)
            if matches:
                return pd.to_numeric(df[cols_lower[matches[0]]], errors="coerce")
        return None

    async def run(self, data: pd.DataFrame, context: Optional[str] = None) -> Dict:
        df         = data.copy()
        user_input = context or ""
        language   = self.detect_language(user_input)
        schema     = detect_schema(df)
        kpis: Dict[str, Any] = {}
 
        if schema == "transaction_log":
            kpis = self._calc_transaction_kpis(df)
        elif schema == "balance_sheet":
            kpis = self._calc_balance_sheet_kpis(df)
        else:
            kpis = self._calc_transaction_kpis(df)
            if not kpis:
                kpis = self._calc_balance_sheet_kpis(df)
 
        schema_summary = get_schema_summary(df, schema)
 
        if not kpis:
            return self._format_result("KPIEngine", {
                "language_detected": language,
                "schema_detected":   schema,
                "calculated_kpis":   {},
                "interpretation":    (
                    "Could not calculate KPIs — no recognisable financial columns found. "
                    f"Columns available: {df.columns.tolist()}"
                ),
                "columns_available": df.columns.tolist()
            })
 
        prompt = f"""You are a financial analyst.
 
Language to respond in: {language}
Data type: {schema}
Data overview: {schema_summary}
 
Calculated KPIs:
{kpis}
 
STRICT RULES:
- Interpret ONLY the KPIs listed above. Do not invent or suggest additional ones.
- One sentence per KPI: state whether it is healthy, average, or concerning and why.
- For transaction logs, note if cost-only rows (zero revenue) affect totals.
- Do NOT add recommendations or action plans.
- Maximum 120 words."""
 
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
 
        return self._format_result("KPIEngine", {
            "language_detected":  language,
            "schema_detected":    schema,
            "calculated_kpis":    kpis,
            "interpretation":     response.content,
            "columns_available":  df.columns.tolist()
        })
 
    def _calc_transaction_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        kpis: Dict[str, Any] = {}
 
        revenue_col = self.find_column(df, ["revenue", "sales", "income"])
        cost_col    = self.find_column(df, ["cost", "cogs", "expense"])
        mktg_col    = self.find_column(df, ["marketing", "marketing_spend", "ad_spend"])
 
        if revenue_col is None:
            return kpis
 
        total_revenue = safe_float(revenue_col.sum())
        if total_revenue is not None:
            kpis["total_revenue"] = total_revenue
 
        if cost_col is not None:
            total_cost = safe_float(cost_col.sum())
            if total_cost is not None:
                kpis["total_cost"] = total_cost
 
            # Gross margin only on rows where revenue > 0
            revenue_mask = revenue_col > 0
            if revenue_mask.any():
                rev_rows  = revenue_col[revenue_mask]
                cost_rows = cost_col[revenue_mask]
                gm = safe_float(((rev_rows - cost_rows) / rev_rows * 100).mean())
                if gm is not None:
                    kpis["gross_margin_pct"] = gm
 
            net_profit = safe_float(revenue_col.sum() - cost_col.sum())
            if net_profit is not None:
                kpis["net_profit"] = net_profit
 
        if mktg_col is not None:
            total_mktg = safe_float(mktg_col.sum())
            if total_mktg is not None:
                kpis["total_marketing_spend"] = total_mktg
 
            mktg_mask = (revenue_col > 0) & (mktg_col > 0)
            if mktg_mask.any():
                roi = safe_float(
                    ((revenue_col[mktg_mask] - mktg_col[mktg_mask]) / mktg_col[mktg_mask] * 100).mean()
                )
                if roi is not None:
                    kpis["marketing_roi_pct"] = roi
 
        cat_col = next(
            (c for c in df.columns if c.lower() in {"category", "type", "description"}),
            None
        )
        if cat_col:
            breakdown = {}
            for cat, group in df.groupby(cat_col):
                rev = safe_float(pd.to_numeric(group[revenue_col.name], errors="coerce").sum())
                if rev is not None:
                    breakdown[str(cat)] = rev
            if breakdown:
                kpis["revenue_by_category"] = breakdown
 
        return kpis
 
    def _calc_balance_sheet_kpis(self, df: pd.DataFrame) -> Dict[str, Any]:
        kpis: Dict[str, Any] = {}
 
        def store(key, num, den, pct=False):
            if num is None or den is None:
                return
            val = safe_float((num / den.replace(0, float("nan")) * (100 if pct else 1)).mean())
            if val is not None:
                kpis[key] = val
 
        revenue = self.find_column(df, ["revenue", "sales", "income"])
        cost    = self.find_column(df, ["cost", "cogs", "expense"])
        net_inc = self.find_column(df, ["net_income", "net_profit", "profit"])
        curr_a  = self.find_column(df, ["current_asset", "current_assets"])
        curr_l  = self.find_column(df, ["current_liability", "current_liab"])
        equity  = self.find_column(df, ["equity", "stockholder", "shareholder_equity"])
        debt    = self.find_column(df, ["debt", "total_debt", "borrowings"])
 
        if revenue is not None and cost is not None:
            store("gross_margin_pct", revenue - cost, revenue, pct=True)
        if net_inc is not None and revenue is not None:
            store("net_margin_pct", net_inc, revenue, pct=True)
        if curr_a is not None and curr_l is not None:
            store("current_ratio", curr_a, curr_l)
        if net_inc is not None and equity is not None:
            store("return_on_equity_pct", net_inc, equity, pct=True)
        if debt is not None and equity is not None:
            store("debt_to_equity", debt, equity)
 
        return kpis
 