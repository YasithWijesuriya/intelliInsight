# backend/app/utils/schema_detector.py
# PURPOSE: Detect what kind of data the DataFrame contains so agents
# can adapt their analysis instead of assuming a balance sheet.

import pandas as pd
from typing import Literal

DataSchema = Literal["transaction_log", "balance_sheet", "time_series", "unknown"]


def detect_schema(df: pd.DataFrame) -> DataSchema:
    """
    Inspect column names and data patterns to classify the DataFrame type.
    Returns one of: 'transaction_log', 'balance_sheet', 'time_series', 'unknown'
    """
    cols = [c.lower().replace(" ", "_") for c in df.columns]
    col_set = set(cols)

    # Transaction log signals
    transaction_signals = {"category", "transaction_id", "txn", "type", "description"}
    has_transaction_cols = bool(col_set & transaction_signals)

    # Balance sheet signals
    balance_sheet_signals = {"total_asset", "equity", "current_liability",
                             "long_term_debt", "retained_earnings", "stockholder"}
    has_balance_cols = bool(col_set & balance_sheet_signals)

    # Time series signals
    has_date = any("date" in c or "month" in c or "period" in c or "year" in c for c in cols)
    has_revenue = any("revenue" in c or "sales" in c or "income" in c for c in cols)

    if has_transaction_cols and has_revenue:
        return "transaction_log"
    if has_balance_cols:
        return "balance_sheet"
    if has_date and has_revenue:
        return "time_series"
    return "unknown"


def get_schema_summary(df: pd.DataFrame, schema: DataSchema) -> str:
    """Return a plain-text description of the data for use in prompts."""
    cols = df.columns.tolist()
    rows = len(df)

    if schema == "transaction_log":
        # Summarise by category if a category column exists
        cat_col = next(
            (c for c in df.columns if c.lower() in {"category", "type", "description"}),
            None
        )
        if cat_col:
            summary = df.groupby(cat_col).agg(
                row_count=(df.columns[0], "count")
            ).reset_index().to_string(index=False)
            return (
                f"Transaction log with {rows} rows and columns: {cols}\n"
                f"Categories present:\n{summary}"
            )

    return f"DataFrame with {rows} rows and columns: {cols}"