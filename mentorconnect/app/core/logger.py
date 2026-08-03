"""
app/core/logger.py
-------------------
Centralized logging configuration using loguru.
- Writes structured logs to rotating files (separate for app + errors).
- Also logs to console in development.
- Used everywhere instead of print() statements.
"""

import sys
import os
from loguru import logger
from app.core.config import settings

# Ensure log directory exists
os.makedirs(settings.LOG_DIR, exist_ok=True)

# Remove default handler to fully control sinks
logger.remove()

# Console sink - human readable, colorized (development friendly)
logger.add(
    sys.stdout,
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    colorize=True,
    backtrace=True,
    diagnose=settings.APP_DEBUG,
)

# General application log file - rotates daily, keeps N days
logger.add(
    os.path.join(settings.LOG_DIR, "app_{time:YYYY-MM-DD}.log"),
    level=settings.LOG_LEVEL,
    rotation="00:00",
    retention=f"{settings.LOG_RETENTION_DAYS} days",
    compression="zip",
    enqueue=True,  # thread/process safe
    backtrace=True,
    diagnose=False,
)

# Dedicated error log file - only ERROR and above, easier for alerting/monitoring
logger.add(
    os.path.join(settings.LOG_DIR, "error_{time:YYYY-MM-DD}.log"),
    level="ERROR",
    rotation="00:00",
    retention=f"{settings.LOG_RETENTION_DAYS} days",
    compression="zip",
    enqueue=True,
    backtrace=True,
    diagnose=False,
)

__all__ = ["logger"]
