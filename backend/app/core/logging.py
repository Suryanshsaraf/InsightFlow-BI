# Logging configurations for structured app tracking
"""
Structured logging configuration using ``structlog``.
"""

import logging
import sys
from typing import Any, Dict

import structlog

from app.config import get_settings

settings = get_settings()


def configure_logging() -> None:
    """Configure structlog logging for the application."""
    
    # Configure the standard logging library to direct output to stdout
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.getLevelName(settings.log_level.upper()),
    )
    
    # Configure structlog processors
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]
    
    if settings.debug:
        # Development / Human-readable console formatting
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True)
        ]
    else:
        # Production JSON formatting
        processors = shared_processors + [
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer(),
        ]
        
    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


# Export a default bound logger
logger = structlog.get_logger("insightflow")
