# PURPOSE: Loads Excel/CSV files into a Pandas DataFrame
# This is always the FIRST step in structured data processing
# DataFrame = a table in Python (like Excel in code)

import pandas as pd
from typing import Optional
from base import BaseAgent

class StructuredIngestionAgent(BaseAgent):

    def __init__(self):
        super().__init__("StructuredIngestionAgent")

    async def run(self, data: str,context=None) -> dict:
        file_path = data
        df = self.load_file(file_path)
     
        if df is None:
            return self._format_result("StructuredIngestionAgent",
                {"error": "Could not load file"}, confidence=0.0)

        # Basic info about the loaded data
        return self._format_result("StructuredIngestionAgent", {
            "shape":   list(df.shape),     # [rows, columns]
            "columns": df.columns.tolist(),
            "dtypes":  {col: str(dtype) for col, dtype in df.dtypes.items()},
            "preview": df.head(3).to_dict(orient="records")
            # head(3) = first 3 rows as list of dicts
        })

    def load_file(self, file_path: str) -> Optional[pd.DataFrame]:
        try:
            if file_path.endswith(".csv"):
                df = pd.read_csv(file_path)  
            elif file_path.endswith((".xlsx", ".xls")):
                df = pd.read_excel(file_path)
            else:
                return None

            # Clean column names: strip spaces, lowercase
            df.columns = [c.strip().lower().replace(" ", "_")
                          for c in df.columns]
            return df

        except Exception as e:
            print(f"Ingestion error: {e}")
            return None