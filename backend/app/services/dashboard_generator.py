"""
Dashboard and chart auto-generation service.
"""

from typing import Any, Dict, List, Optional
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.logging import logger
from app.models.chart import Chart, ChartType
from app.models.dashboard import Dashboard
from app.models.dataset import Dataset
from app.services.chart_recommender import ChartRecommenderService
from app.services.kpi_detector import KPIDetectorService

settings = get_settings()


class DashboardGeneratorService:
    """Orchestrates automatic dashboard generation from dataset profiling."""
    
    @classmethod
    async def run_query(
        cls, db: AsyncSession, query_str: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Utility function to execute SQL and return list of dicts."""
        res = await db.execute(text(query_str), params or {})
        keys = res.keys()
        return [dict(zip(keys, row)) for row in res.fetchall()]

    @classmethod
    async def compute_chart_data(
        cls,
        db: AsyncSession,
        table_name: str,
        chart_type: ChartType,
        x_col: Optional[str],
        y_col: Optional[str],
        agg: Optional[str],
    ) -> Dict[str, Any]:
        """
        Query the dynamic table to aggregate and fetch data for a specific chart.
        """
        schema_prefix = "" if settings.is_sqlite else f"{settings.user_data_schema}."
        
        # 1. Table or Raw Data
        if chart_type == ChartType.TABLE or not x_col or not y_col:
            q = f"SELECT * FROM {schema_prefix}{table_name} LIMIT 100"
            rows = await cls.run_query(db, q)
            return {"rows": rows}
            
        # 2. Scatter Plot (no aggregation)
        if chart_type == ChartType.SCATTER or not agg:
            q = f"SELECT {x_col}, {y_col} FROM {schema_prefix}{table_name} WHERE {x_col} IS NOT NULL AND {y_col} IS NOT NULL LIMIT 500"
            rows = await cls.run_query(db, q)
            return {"rows": rows}
            
        # 3. Aggregated Charts (Bar, Line, Area, Pie/Donut)
        agg_expr = f"{agg.upper()}({y_col})"
        q = f"""
            SELECT {x_col}, {agg_expr} AS {y_col}
            FROM {schema_prefix}{table_name}
            WHERE {x_col} IS NOT NULL AND {y_col} IS NOT NULL
            GROUP BY {x_col}
            ORDER BY {y_col} DESC
            LIMIT 100
        """
        try:
            rows = await cls.run_query(db, q)
            
            # If it's a line/area/scatter chart, sorting by X column makes more sense than Y
            # e.g. sorting dates chronologically rather than by aggregate values
            if chart_type in [ChartType.LINE, ChartType.AREA]:
                rows.sort(key=lambda r: str(r[x_col]) if r[x_col] is not None else "")
                
            return {"rows": rows}
        except Exception as e:
            logger.error(
                "Failed to compute chart data",
                table_name=table_name,
                x=x_col,
                y=y_col,
                error=str(e),
            )
            return {"rows": [], "error": str(e)}

    @classmethod
    async def generate_dashboard(
        cls, db: AsyncSession, dataset: Dataset
    ) -> Dashboard:
        """
        Auto-generate a complete dashboard with charts, layout, and KPI data.
        """
        if not dataset.table_name or not dataset.column_schema or not dataset.statistics:
            raise ValueError("Dataset is not fully processed or lacks schema metadata.")
            
        logger.info("Generating dashboard", dataset_id=dataset.id, table_name=dataset.table_name)
        
        # 1. Compute & save KPIs
        kpis = await KPIDetectorService.compute_kpis(
            db, dataset.table_name, dataset.column_schema, limit=4
        )
        dataset.detected_kpis = {"kpis": kpis}
        db.add(dataset)
        
        # 2. Recommended charts
        recommended_charts = ChartRecommenderService.recommend_charts(
            dataset.column_schema, dataset.statistics
        )
        
        # 3. Create Dashboard
        dashboard = Dashboard(
            title=f"Dashboard for {dataset.name}",
            description=dataset.description or f"Auto-generated analytics dashboard for {dataset.file_name}.",
            is_auto_generated=True,
            owner_id=dataset.owner_id,
            dataset_id=dataset.id,
        )
        
        db.add(dashboard)
        await db.flush()  # Populates dashboard.id
        
        # 4. Generate Layout & Charts
        # We layout using standard y_cursor increments
        # y=0 is reserved for the KPI cards in the frontend, so we start charts at y=2
        y_cursor = 2
        layout_config: Dict[str, Any] = {"items": []}
        
        # Grid Coordinates Logic
        # - Top Row: Line trend (width 8) + Pie breakdown (width 4) -> height 4
        # - Middle Row: Bar comparisons (width 6) + Scatter/Second Bar (width 6) -> height 4
        # - Bottom Row: Raw data table (width 12) -> height 5
        
        has_trend = any(c["chart_type"] == ChartType.LINE for c in recommended_charts)
        has_pie = any(c["chart_type"] in [ChartType.PIE, ChartType.DONUT] for c in recommended_charts)
        
        charts_to_create: List[Dict[str, Any]] = []
        
        # Top row pairing
        current_x = 0
        if has_trend:
            trend_idx = next(i for i, c in enumerate(recommended_charts) if c["chart_type"] == ChartType.LINE)
            trend_chart = recommended_charts.pop(trend_idx)
            trend_chart.update({"x": 0, "y": y_cursor, "w": 8, "h": 4})
            charts_to_create.append(trend_chart)
            current_x = 8
            
        if has_pie and recommended_charts:
            pie_idx = next(i for i, c in enumerate(recommended_charts) if c["chart_type"] in [ChartType.PIE, ChartType.DONUT])
            pie_chart = recommended_charts.pop(pie_idx)
            pie_chart.update({"x": current_x, "y": y_cursor, "w": 12 - current_x, "h": 4})
            charts_to_create.append(pie_chart)
            y_cursor += 4
        elif has_trend:
            # If trend exists but no pie, trend takes full width
            charts_to_create[-1].update({"w": 12})
            y_cursor += 4
            
        # Middle row pairing (take next 2 charts)
        middle_row_charts = [c for c in recommended_charts if c["chart_type"] != ChartType.TABLE][:2]
        for i, chart in enumerate(middle_row_charts):
            recommended_charts.remove(chart)
            chart.update({"x": i * 6, "y": y_cursor, "w": 6, "h": 4})
            charts_to_create.append(chart)
            
        if middle_row_charts:
            y_cursor += 4
            
        # Bottom row: Data Table
        table_charts = [c for c in recommended_charts if c["chart_type"] == ChartType.TABLE]
        if table_charts:
            table_chart = table_charts[0]
            recommended_charts.remove(table_chart)
            table_chart.update({"x": 0, "y": y_cursor, "w": 12, "h": 5})
            charts_to_create.append(table_chart)
            y_cursor += 5
            
        # Create and compute data for each chart
        for idx, chart_in in enumerate(charts_to_create):
            # Compute data
            cached_data = await cls.compute_chart_data(
                db,
                dataset.table_name,
                chart_in["chart_type"],
                chart_in["x_column"],
                chart_in["y_column"],
                chart_in["aggregation"],
            )
            
            new_chart = Chart(
                title=chart_in["title"],
                description=chart_in.get("description"),
                chart_type=chart_in["chart_type"],
                x_column=chart_in["x_column"],
                y_column=chart_in["y_column"],
                aggregation=chart_in["aggregation"],
                config=chart_in["config"],
                cached_data=cached_data,
                position_x=chart_in["x"],
                position_y=chart_in["y"],
                width=chart_in["w"],
                height=chart_in["h"],
                is_auto_generated=True,
                owner_id=dataset.owner_id,
                dataset_id=dataset.id,
                dashboard_id=dashboard.id,
            )
            
            db.add(new_chart)
            await db.flush()  # Populates new_chart.id
            
            # Save react-grid-layout coordinates in dashboard configuration
            layout_config["items"].append({
                "i": new_chart.id,
                "x": chart_in["x"],
                "y": chart_in["y"],
                "w": chart_in["w"],
                "h": chart_in["h"],
            })
            
        dashboard.layout_config = layout_config
        db.add(dashboard)
        await db.commit()
        await db.refresh(dashboard)
        
        logger.info("Dashboard generated successfully", dashboard_id=dashboard.id)
        return dashboard
