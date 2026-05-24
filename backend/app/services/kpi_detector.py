"""
Service for detecting KPI candidates from a dataset and computing their values.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging import logger

settings = get_settings()


class KPIDetectorService:
    """Detects and computes Key Performance Indicators from datasets."""
    
    @staticmethod
    def detect_kpi_candidates(
        column_schema: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Analyze columns and return a list of potential KPIs.
        """
        candidates: List[Dict[str, Any]] = []
        
        # 1. Always add Total Records
        candidates.append({
            "column": "*",
            "aggregation": "count",
            "label": "Total Records",
            "format": "number",
            "priority": 10,
        })
        
        # Keywords lists
        currency_keywords = ["revenue", "sales", "amount", "price", "cost", "profit", "spend", "income"]
        quantity_keywords = ["count", "quantity", "units", "items", "number_of"]
        rate_keywords = ["rate", "ratio", "percentage", "percent", "pct", "margin", "ctr", "roi"]
        
        for col_name, col_meta in column_schema.items():
            if col_meta["inferred_type"] != "numeric":
                continue
                
            label = col_name.replace("_", " ").title()
            
            # Currency detection
            if any(kw in col_name for kw in currency_keywords):
                candidates.append({
                    "column": col_name,
                    "aggregation": "sum",
                    "label": f"Total {label}",
                    "format": "currency",
                    "priority": 9,
                })
                # Also add average for price/cost
                if "price" in col_name or "cost" in col_name:
                    candidates.append({
                        "column": col_name,
                        "aggregation": "avg",
                        "label": f"Average {label}",
                        "format": "currency",
                        "priority": 7,
                    })
                    
            # Quantity detection
            elif any(kw in col_name for kw in quantity_keywords):
                candidates.append({
                    "column": col_name,
                    "aggregation": "sum",
                    "label": f"Total {label}",
                    "format": "number",
                    "priority": 8,
                })
                
            # Rate detection
            elif any(kw in col_name for kw in rate_keywords):
                candidates.append({
                    "column": col_name,
                    "aggregation": "avg",
                    "label": f"Average {label}",
                    "format": "percentage",
                    "priority": 8,
                })
                
            # Fallback numeric
            else:
                candidates.append({
                    "column": col_name,
                    "aggregation": "sum",
                    "label": f"Total {label}",
                    "format": "number",
                    "priority": 5,
                })
                candidates.append({
                    "column": col_name,
                    "aggregation": "avg",
                    "label": f"Average {label}",
                    "format": "number",
                    "priority": 4,
                })
                
        # Sort candidates by priority desc
        candidates.sort(key=lambda x: x["priority"], reverse=True)
        return candidates

    @classmethod
    async def compute_kpis(
        self,
        db: AsyncSession,
        table_name: str,
        column_schema: Dict[str, Dict[str, Any]],
        limit: int = 4,
    ) -> List[Dict[str, Any]]:
        """
        Detect and compute values for the top N KPIs.
        
        Includes trend analysis (change percentage) if a datetime column exists.
        """
        candidates = self.detect_kpi_candidates(column_schema)
        selected_kpis = candidates[:limit]
        
        # Find first datetime column for trend analysis
        date_col = None
        for col_name, col_meta in column_schema.items():
            if col_meta["inferred_type"] == "datetime":
                date_col = col_name
                break
                
        computed_kpis: List[Dict[str, Any]] = []
        schema_prefix = "" if settings.is_sqlite else f"{settings.user_data_schema}."
        
        for kpi in selected_kpis:
            col = kpi["column"]
            agg = kpi["aggregation"].upper()
            
            # Build aggregate expression
            agg_expr = "COUNT(*)" if col == "*" else f"{agg}({col})"
            
            try:
                # 1. Compute overall value
                query_str = f"SELECT {agg_expr} FROM {schema_prefix}{table_name}"
                res = await db.execute(text(query_str))
                val = res.scalar()
                
                # Convert to float/int
                overall_value = float(val) if val is not None else 0.0
                if overall_value.is_integer():
                    overall_value = int(overall_value)
                    
                change_percent = None
                change_direction = "neutral"
                
                # 2. Compute change percent if date column is present
                if date_col and col != "*":
                    # Get min and max dates
                    date_res = await db.execute(
                        text(f"SELECT MIN({date_col}), MAX({date_col}) FROM {schema_prefix}{table_name}")
                    )
                    min_date, max_date = date_res.fetchone()
                    
                    if min_date and max_date and min_date != max_date:
                        # Find midpoint of dates
                        # Since dates are ISO strings or Datetime objects:
                        # In SQLite/PostgreSQL, we can let Pandas do date logic or query midpoint
                        # Simplest way: split based on midpoint string or timestamp.
                        # For SQL query:
                        # SQLite: datetime(strftime('%s', min) + (strftime('%s', max) - strftime('%s', min))/2, 'unixepoch')
                        # For standard application logic, we can compute midpoint in Python and query.
                        
                        try:
                            # Let's do simple midpoint computation in Python
                            import pandas as pd
                            p_min = pd.to_datetime(min_date)
                            p_max = pd.to_datetime(max_date)
                            p_mid = p_min + (p_max - p_min) / 2
                            mid_str = p_mid.isoformat()
                            
                            # Query current (recent half) and previous (older half)
                            curr_query = f"SELECT {agg_expr} FROM {schema_prefix}{table_name} WHERE {date_col} >= :mid"
                            prev_query = f"SELECT {agg_expr} FROM {schema_prefix}{table_name} WHERE {date_col} < :mid"
                            
                            curr_res = await db.execute(text(curr_query), {"mid": mid_str})
                            prev_res = await db.execute(text(prev_query), {"mid": mid_str})
                            
                            curr_val = curr_res.scalar()
                            prev_val = prev_res.scalar()
                            
                            curr_val = float(curr_val) if curr_val is not None else 0.0
                            prev_val = float(prev_val) if prev_val is not None else 0.0
                            
                            if prev_val > 0:
                                change_percent = round(((curr_val - prev_val) / prev_val) * 100, 2)
                                if change_percent > 0:
                                    change_direction = "up"
                                elif change_percent < 0:
                                    change_direction = "down"
                        except Exception as inner_e:
                            logger.warning("Could not compute trend for KPI", kpi=kpi, error=str(inner_e))
                            
                computed_kpis.append({
                    "column": col,
                    "aggregation": kpi["aggregation"],
                    "label": kpi["label"],
                    "value": overall_value,
                    "format": kpi["format"],
                    "change_percent": change_percent,
                    "change_direction": change_direction,
                })
                
            except Exception as e:
                logger.error("Failed to compute KPI", kpi=kpi, error=str(e))
                # Add a default / placeholder so the application doesn't crash
                computed_kpis.append({
                    "column": col,
                    "aggregation": kpi["aggregation"],
                    "label": kpi["label"],
                    "value": 0,
                    "format": kpi["format"],
                    "change_percent": None,
                    "change_direction": "neutral",
                })
                
        return computed_kpis
