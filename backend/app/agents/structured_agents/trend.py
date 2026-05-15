# PURPOSE: Detects trends in numerical data

import math
import pandas as pd
from typing import Dict, Optional
from langchain_core.messages import HumanMessage
from app.agents.base import BaseAgent
from app.utils.schema_detector import detect_schema


def safe_float(value, decimals: int = 4) -> Optional[float]:
    try:
        v = float(value)
        if math.isnan(v) or math.isinf(v):
            return None
        return round(v, decimals)
    except (TypeError, ValueError):
        return None


class TrendAgent(BaseAgent):

    def __init__(self):
        super().__init__("TrendAgent")

    async def run(self, data: pd.DataFrame, context=None) -> Dict:
        df     = data.copy()
        schema = detect_schema(df)
        stats  = {}

        if schema == "transaction_log":
            stats = self._transaction_trends(df)
        else:
            stats = self._numeric_trends(df)

        if not stats:
            return self._format_result("TrendAgent", {
                "error": "No numeric data found to analyse trends."
            })

        prompt = f"""You are a data analyst. Report what these statistics show.

Data type: {schema}
Statistics:
{stats}

STRICT RULES:
- Report only what the numbers directly show. Do not speculate about causes.
- Every observation must reference a specific number from the stats above.
- If a metric has only 1 or 2 data points, say "insufficient data for trend".
- Maximum 3 bullet points. Maximum 100 words total.
- Do not add recommendations."""

        response = await self.llm.ainvoke([HumanMessage(content=prompt)])

        return self._format_result("TrendAgent", {
            "schema_detected": schema,
            "statistics":      stats,
            "ai_analysis":     response.content
        })

    def _transaction_trends(self, df: pd.DataFrame) -> Dict:
        """For transaction logs: analyse by category and over time."""
        stats = {}

        # Find key columns
        revenue_col = next((c for c in df.columns if "revenue" in c.lower() or "sales" in c.lower()), None)
        cost_col    = next((c for c in df.columns if "cost" in c.lower() or "cogs" in c.lower()), None)
        mktg_col    = next((c for c in df.columns if "marketing" in c.lower()), None)
        cat_col     = next((c for c in df.columns if c.lower() in {"category", "type", "description"}), None)
        date_col    = next((c for c in df.columns if "date" in c.lower()), None)

        # Revenue trend over time (only revenue-generating rows)
        if revenue_col and date_col:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
            revenue_rows = df[pd.to_numeric(df[revenue_col], errors="coerce") > 0].copy()
            if len(revenue_rows) >= 2:
                revenue_rows = revenue_rows.sort_values(date_col)
                rev_series   = pd.to_numeric(revenue_rows[revenue_col], errors="coerce")
                first = safe_float(rev_series.iloc[0])
                last  = safe_float(rev_series.iloc[-1])
                if first and last and first != 0:
                    stats["revenue_trend"] = {
                        "first_transaction": first,
                        "last_transaction":  last,
                        "change":            safe_float(last - first),
                        "pct_change":        safe_float((last - first) / first * 100),
                        "data_points":       len(revenue_rows)
                    }

        # Category breakdown
        if cat_col and revenue_col:
            cat_stats = {}
            for cat, group in df.groupby(cat_col):
                rev  = safe_float(pd.to_numeric(group[revenue_col], errors="coerce").sum())
                cost = safe_float(pd.to_numeric(group[cost_col], errors="coerce").sum()) if cost_col else None
                cat_stats[str(cat)] = {"total_revenue": rev, "total_cost": cost}
            stats["by_category"] = cat_stats

        # Marketing spend trend
        if mktg_col and date_col and len(df) >= 2:
            mktg_series = pd.to_numeric(df.sort_values(date_col)[mktg_col], errors="coerce").dropna()
            if len(mktg_series) >= 2:
                stats["marketing_spend"] = {
                    "min":   safe_float(mktg_series.min()),
                    "max":   safe_float(mktg_series.max()),
                    "total": safe_float(mktg_series.sum()),
                    "data_points": len(mktg_series)
                }

        return stats

    def _numeric_trends(self, df: pd.DataFrame) -> Dict:
        """Fallback for balance sheets and generic numeric data."""
        stats = {}
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

        for col in numeric_cols[:6]:
            series = df[col].dropna()
            if len(series) < 2:
                continue
            first = safe_float(series.iloc[0])
            last  = safe_float(series.iloc[-1])
            pct = (
                safe_float((last - first) / first * 100)
                if first is not None and last is not None and first != 0
                else None
            )

            stats[col] = {
                "min":          safe_float(series.min()),
                "max":          safe_float(series.max()),
                "mean":         safe_float(series.mean()),
                "first_value":  first,
                "last_value":   last,
                "total_change": safe_float(last - first) if first and last else None,
                "pct_change":   pct,
            }

        return stats