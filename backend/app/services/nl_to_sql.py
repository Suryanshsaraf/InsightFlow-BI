"""
Natural Language to SQL conversion service.
"""

from typing import Any, Dict, List
from openai import AsyncOpenAI

from app.config import get_settings
from app.core.exceptions import ValidationException
from app.core.logging import logger

settings = get_settings()


class NLToSQLService:
    """Translates natural language questions into safe SQL queries using OpenAI."""
    
    @staticmethod
    def _get_client() -> AsyncOpenAI:
        """Initialize AsyncOpenAI client if key is configured."""
        if not settings.openai_api_key:
            raise ValidationException(
                "OpenAI API Key is not configured on the backend. Please add it to your .env file."
            )
        return AsyncOpenAI(api_key=settings.openai_api_key)

    @classmethod
    async def translate_query(
        cls,
        table_name: str,
        column_schema: Dict[str, Dict[str, Any]],
        statistics: Dict[str, Dict[str, Any]],
        user_question: str,
    ) -> str:
        """
        Convert a natural language question into a SQL query based on the table schema.
        """
        client = cls.get_client_or_raise()
        
        # 1. Format columns and types for the prompt
        columns_info: List[str] = []
        for col_name, col_meta in column_schema.items():
            t = col_meta["inferred_type"]
            columns_info.append(f"- {col_name} ({t})")
            
        columns_str = "\n".join(columns_info)
        
        # 2. Get sample top values/stats to help the LLM write filters
        sample_stats: List[str] = []
        for col_name, stats in statistics.items():
            if "top_values" in stats:
                top_vals = [str(x["value"]) for x in stats["top_values"][:3]]
                sample_stats.append(f"- {col_name} sample values: {', '.join(top_vals)}")
                
        sample_stats_str = "\n".join(sample_stats)
        
        # 3. Determine database dialetic
        dialect = "SQLite" if settings.is_sqlite else "PostgreSQL"
        schema_desc = table_name if settings.is_sqlite else f"{settings.user_data_schema}.{table_name}"
        
        system_prompt = f"""You are a senior data architect and SQL expert.
Convert the user's natural language question into a valid, safe SQL SELECT query for a {dialect} database.

Target Table Name: {schema_desc}
Available Columns and Inferred Types:
{columns_str}

Sample/Top Column Values (use these for string filters):
{sample_stats_str}

RULES:
1. Return ONLY the raw SQL query. Do NOT wrap it in markdown code blocks, do NOT write explanations, do NOT write markdown tags.
2. Only SELECT queries are allowed.
3. Always use the exact table name provided: {schema_desc}
4. Always qualify column names. Use double quotes around column names if they match reserved SQL keywords.
5. Use LIMIT 100 unless the user specifies otherwise.
6. Use appropriate aggregations (SUM, AVG, COUNT, etc.) and GROUP BY statements when numerical metrics are compared across categories.
"""
        
        try:
            logger.info("Translating NL query to SQL", table_name=table_name, question=user_question)
            
            response = await client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Question: {user_question}"},
                ],
                temperature=0.0,
                max_tokens=settings.openai_max_tokens,
            )
            
            sql_query = response.choices[0].message.content.strip()
            
            # Clean up potential markdown formatting if the model ignored instructions
            if sql_query.startswith("```"):
                # Strip out ```sql ... ```
                sql_query = sql_query.replace("```sql", "", 1)
                sql_query = sql_query.replace("```", "", 1)
                sql_query = sql_query.strip()
                
            logger.info("Successfully translated SQL query", sql=sql_query)
            return sql_query
            
        except Exception as e:
            logger.exception("Failed to translate natural language to SQL", question=user_question)
            raise ValidationException(f"AI translation failed: {str(e)}")

    @classmethod
    def get_client_or_raise(cls) -> AsyncOpenAI:
        """Check key and return client."""
        return cls._get_client()
