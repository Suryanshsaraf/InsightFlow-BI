"""
CSV data cleaning, type inference, and statistics computation service.
"""

import math
import re
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from app.core.exceptions import CSVProcessingException
from app.core.logging import logger


class CSVProcessorService:
    """Service for cleaning, typing, and profiling CSV files."""
    
    @staticmethod
    def normalize_column_name(name: str) -> str:
        """
        Normalize column names to be database friendly.
        
        - Lowercase
        - Replace spaces and hyphens with underscores
        - Remove non-alphanumeric characters except underscore
        - Strip leading/trailing whitespaces/underscores
        """
        name = str(name).strip().lower()
        name = re.sub(r"[\s\-]+", "_", name)
        name = re.sub(r"[^\w]", "", name)
        name = re.sub(r"^_+|_+$", "", name)
        
        # If column name starts with a digit, prefix with col_
        if name and name[0].isdigit():
            name = f"col_{name}"
            
        return name or "unnamed_column"

    @classmethod
    def clean_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Perform standard dataframe cleaning:
        1. Normalize column names (and handle duplicate names)
        2. Remove fully empty rows
        3. Remove fully empty columns
        4. Trim whitespace from string columns
        """
        # 1. Normalize and deduplicate headers
        norm_cols = [cls.normalize_column_name(col) for col in df.columns]
        dedup_cols: List[str] = []
        counts: Dict[str, int] = {}
        for col in norm_cols:
            if col in counts:
                counts[col] += 1
                dedup_cols.append(f"{col}_{counts[col]}")
            else:
                counts[col] = 0
                dedup_cols.append(col)
                
        df.columns = dedup_cols
        
        # 2. Drop fully empty rows and columns
        df = df.dropna(how="all")
        df = df.dropna(axis=1, how="all")
        
        # 3. Trim string columns
        for col in df.select_dtypes(include=["object", "string"]).columns:
            df[col] = df[col].astype(str).str.strip()
            
        return df

    @staticmethod
    def infer_column_type(series: pd.Series) -> str:
        """
        Infer column type: "numeric" | "datetime" | "boolean" | "categorical" | "text"
        """
        # Drop nulls for checking types
        non_null = series.dropna()
        if len(non_null) == 0:
            return "text"
            
        # Check boolean
        if pd.api.types.is_bool_dtype(series):
            return "boolean"
            
        # Check boolean-like strings
        unique_vals = set(non_null.astype(str).str.lower().unique())
        boolean_sets = [{"true", "false"}, {"yes", "no"}, {"1", "0"}, {"t", "f"}]
        if unique_vals.issubset(set().union(*boolean_sets)) and len(unique_vals) <= 2:
            return "boolean"
            
        # Check numeric
        if pd.api.types.is_numeric_dtype(series):
            return "numeric"
            
        # Try datetime conversion (if >80% parse successfully)
        # We check a sample if the series is very large to avoid performance issues
        sample_size = min(len(non_null), 1000)
        sample = non_null.sample(n=sample_size, random_state=42)
        try:
            parsed = pd.to_datetime(sample, errors="coerce")
            parsed_ratio = parsed.notnull().sum() / sample_size
            if parsed_ratio >= 0.8:
                return "datetime"
        except Exception:
            pass
            
        # Check categorical vs text based on cardinality
        cardinality = len(unique_vals)
        total_count = len(series)
        
        if cardinality <= 20 or (cardinality / total_count < 0.2 and cardinality < 100):
            return "categorical"
            
        return "text"

    @classmethod
    def analyze_dataset(
        cls, file_path: str
    ) -> Tuple[pd.DataFrame, Dict[str, Any], Dict[str, Any], Dict[str, Any]]:
        """
        Load CSV, clean, infer schema, and generate column stats and sample data.
        
        Returns:
            df: Cleaned pandas DataFrame
            column_schema: Map of column name to metadata (original name, inferred type, etc.)
            statistics: Map of column name to computed statistics
            sample_data: First 5 rows of cleaned data
        """
        try:
            # First read with auto-detected encoding
            try:
                df = pd.read_csv(file_path, encoding="utf-8")
            except UnicodeDecodeError:
                # Fallback to ISO-8859-1 (Latin-1)
                df = pd.read_csv(file_path, encoding="iso-8859-1")
                
            original_columns = list(df.columns)
            df = cls.clean_dataframe(df)
            
            column_schema: Dict[str, Any] = {}
            statistics: Dict[str, Any] = {}
            
            # Map normalized column name to original name
            col_mapping = {dedup: orig for dedup, orig in zip(df.columns, original_columns)}
            
            for col in df.columns:
                inferred_type = cls.infer_column_type(df[col])
                
                # Basic schema details
                column_schema[col] = {
                    "original_name": col_mapping.get(col, col),
                    "inferred_type": inferred_type,
                    "nullable": df[col].isnull().any(),
                }
                
                # Compute stats
                null_count = int(df[col].isnull().sum())
                null_percentage = float(null_count / len(df))
                
                stats: Dict[str, Any] = {
                    "null_count": null_count,
                    "null_percentage": null_percentage,
                }
                
                # Type-specific stats
                if inferred_type == "numeric":
                    # Convert to numeric to ensure operations succeed
                    num_series = pd.to_numeric(df[col], errors="coerce")
                    # Replace NaN values with None for JSON serialization
                    desc = num_series.describe()
                    stats.update({
                        "min": float(desc["min"]) if not math.isnan(desc["min"]) else None,
                        "max": float(desc["max"]) if not math.isnan(desc["max"]) else None,
                        "mean": float(desc["mean"]) if not math.isnan(desc["mean"]) else None,
                        "median": float(num_series.median()) if not math.isnan(num_series.median()) else None,
                        "std": float(desc["std"]) if not math.isnan(desc["std"]) else None,
                    })
                    
                elif inferred_type == "datetime":
                    dt_series = pd.to_datetime(df[col], errors="coerce")
                    min_date = dt_series.min()
                    max_date = dt_series.max()
                    
                    stats.update({
                        "min_date": min_date.isoformat() if pd.notnull(min_date) else None,
                        "max_date": max_date.isoformat() if pd.notnull(max_date) else None,
                        "range_days": int((max_date - min_date).days) if pd.notnull(min_date) and pd.notnull(max_date) else None,
                    })
                    
                elif inferred_type == "categorical":
                    unique_count = int(df[col].nunique())
                    # Get top 20 categories
                    top_vals = df[col].value_counts().head(20)
                    top_list = [
                        {"value": str(k), "count": int(v)} for k, v in top_vals.items()
                    ]
                    stats.update({
                        "unique_count": unique_count,
                        "top_values": top_list,
                    })
                    
                elif inferred_type == "text":
                    unique_count = int(df[col].nunique())
                    # Text specific stats like lengths
                    lengths = df[col].astype(str).str.len()
                    stats.update({
                        "unique_count": unique_count,
                        "avg_length": float(lengths.mean()) if len(lengths) > 0 else 0,
                        "max_length": int(lengths.max()) if len(lengths) > 0 else 0,
                    })
                    
                elif inferred_type == "boolean":
                    unique_count = int(df[col].nunique())
                    val_counts = df[col].value_counts()
                    stats.update({
                        "unique_count": unique_count,
                        "true_count": int(val_counts.get(True, 0)) if True in val_counts else int(val_counts.get("1", 0)),
                    })
                    
                statistics[col] = stats
                
            # Create sample data (first 5 rows converted to simple Python structures)
            # Replace NaN/NaT with None so it can be serialized to JSON
            sample_df = df.head(5).replace({np.nan: None})
            sample_data = {
                "columns": list(df.columns),
                "rows": sample_df.to_dict(orient="records"),
            }
            
            return df, column_schema, statistics, sample_data
            
        except Exception as e:
            logger.exception("Failed to process CSV file", file_path=file_path)
            raise CSVProcessingException(f"CSV parsing or profiling failed: {str(e)}")
