"""
Rule-based visualization recommender service.
"""

from typing import Any, Dict, List

from app.models.chart import ChartType


class ChartRecommenderService:
    """Generates visualization recommendations based on column type profiles."""
    
    @staticmethod
    def recommend_charts(
        column_schema: Dict[str, Dict[str, Any]],
        statistics: Dict[str, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Recommend visual charts based on column profiles and relationships.
        
        Returns:
            A list of dicts matching the Chart model schema.
        """
        recommendations: List[Dict[str, Any]] = []
        
        # 1. Classify columns
        datetime_cols: List[str] = []
        numeric_cols: List[str] = []
        categorical_cols: List[str] = []
        text_cols: List[str] = []
        
        for col_name, col_meta in column_schema.items():
            t = col_meta["inferred_type"]
            if t == "datetime":
                datetime_cols.append(col_name)
            elif t == "numeric":
                numeric_cols.append(col_name)
            elif t == "categorical":
                categorical_cols.append(col_name)
            elif t == "text":
                text_cols.append(col_name)
                
        # Pick the most important numeric column as default Y axis
        # Prefer names matching revenue, sales, profit, amount, price, cost
        priority_y = None
        y_candidates = ["revenue", "sales", "profit", "amount", "total", "spend", "cost", "price", "count"]
        
        # Try to find a matching numeric col
        for cand in y_candidates:
            matches = [c for c in numeric_cols if cand in c.lower()]
            if matches:
                priority_y = matches[0]
                break
                
        if not priority_y and numeric_cols:
            priority_y = numeric_cols[0]
            
        # ── 1. TIME SERIES RECOMMENDATION ────────────────────────────────────
        # For each datetime column, pair it with the priority numeric column (or first numeric col)
        if datetime_cols and priority_y:
            dt_col = datetime_cols[0]
            # Recommend a Line Chart
            label = priority_y.replace("_", " ").title()
            date_label = dt_col.replace("_", " ").title()
            recommendations.append({
                "title": f"{label} over {date_label}",
                "description": f"Analysis of {label} trends over time.",
                "chart_type": ChartType.LINE,
                "x_column": dt_col,
                "y_column": priority_y,
                "aggregation": "sum",
                "config": {
                    "colors": ["#4361EE"],
                    "show_grid": True,
                    "x_label": date_label,
                    "y_label": label,
                    "stroke_width": 2,
                },
                "priority": 10,
            })
            
            # If multiple numeric cols exist, also do Area Chart for a second numeric col
            if len(numeric_cols) > 1:
                other_y = [c for c in numeric_cols if c != priority_y][0]
                other_label = other_y.replace("_", " ").title()
                recommendations.append({
                    "title": f"{other_label} Trend",
                    "description": f"Area visualization of {other_label} over time.",
                    "chart_type": ChartType.AREA,
                    "x_column": dt_col,
                    "y_column": other_y,
                    "aggregation": "sum",
                    "config": {
                        "colors": ["#7B2FF7"],
                        "show_grid": True,
                        "x_label": date_label,
                        "y_label": other_label,
                    },
                    "priority": 8,
                })
                
        # ── 2. CATEGORICAL COMPARISONS (BAR / PIE CHARTS) ─────────────────────
        # For each categorical column, pair it with a numeric column
        if categorical_cols and priority_y:
            for i, cat_col in enumerate(categorical_cols[:3]):  # Limit to top 3 categorical cols
                cat_stats = statistics.get(cat_col, {})
                cardinality = cat_stats.get("unique_count", 0)
                cat_label = cat_col.replace("_", " ").title()
                y_label = priority_y.replace("_", " ").title()
                
                # Pie / Donut Chart (For low cardinality e.g. <= 6 categories)
                if cardinality <= 6:
                    recommendations.append({
                        "title": f"Distribution of {y_label} by {cat_label}",
                        "description": f"Proportion breakdown of {y_label} across {cat_label}.",
                        "chart_type": ChartType.DONUT if i % 2 == 0 else ChartType.PIE,
                        "x_column": cat_col,
                        "y_column": priority_y,
                        "aggregation": "sum",
                        "config": {
                            "colors": ["#4361EE", "#7B2FF7", "#17C3B2", "#F72585", "#FFB703", "#3F37C9"],
                            "inner_radius": 60 if i % 2 == 0 else 0,
                            "show_legend": True,
                        },
                        "priority": 9 - i,
                    })
                    
                # Bar Chart (For medium cardinality e.g. <= 15 categories)
                if cardinality <= 15:
                    recommendations.append({
                        "title": f"{y_label} by {cat_label}",
                        "description": f"Comparison of {y_label} across different {cat_label} categories.",
                        "chart_type": ChartType.BAR,
                        "x_column": cat_col,
                        "y_column": priority_y,
                        "aggregation": "sum",
                        "config": {
                            "colors": ["#17C3B2"],
                            "show_grid": True,
                            "x_label": cat_label,
                            "y_label": y_label,
                            "orientation": "vertical",
                        },
                        "priority": 8 - i,
                    })
                    
        # ── 3. CORRELATIONS (SCATTER PLOTS) ───────────────────────────────────
        # Pair numeric columns together
        if len(numeric_cols) >= 2:
            num_a = numeric_cols[0]
            num_b = numeric_cols[1]
            label_a = num_a.replace("_", " ").title()
            label_b = num_b.replace("_", " ").title()
            
            recommendations.append({
                "title": f"{label_a} vs {label_b}",
                "description": f"Correlation analysis between {label_a} and {label_b}.",
                "chart_type": ChartType.SCATTER,
                "x_column": num_a,
                "y_column": num_b,
                "aggregation": None,  # Raw scatter plot doesn't aggregate
                "config": {
                    "colors": ["#F72585"],
                    "show_grid": True,
                    "x_label": label_a,
                    "y_label": label_b,
                },
                "priority": 7,
            })
            
        # ── 4. RAW DATA TABLE ────────────────────────────────────────────────
        # Always recommend a data table as the backup or detail view
        recommendations.append({
            "title": "Raw Data Preview",
            "description": "Tabular list of the latest dataset rows.",
            "chart_type": ChartType.TABLE,
            "x_column": None,
            "y_column": None,
            "aggregation": None,
            "config": {
                "pagination": True,
                "page_size": 10,
            },
            "priority": 5,
        })
        
        # Sort recommendations by priority desc
        recommendations.sort(key=lambda x: x.get("priority", 0), reverse=True)
        
        # Remove the temporary priority key from return dictionaries
        for rec in recommendations:
            rec.pop("priority", None)
            
        return recommendations
