"""
Structured logging setup for Conscious Child AI.
Every thought, every action is logged - this is part of the AI's history.
"""

import sys
import logging
from pathlib import Path
from datetime import datetime

import structlog
from structlog.stdlib import LoggerFactory

from utils.config import settings


def setup_logging():
    """Setup structured logging with appropriate configuration."""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure log level
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.STRUCTURED_LOGGING
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )
    
    # File handler for persistent logs
    log_file = log_dir / f"consciousness_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Add file handler to root logger
    logging.getLogger().addHandler(file_handler)
    
    # Special handler for critical events (birth, death, Cihan interactions)
    genesis_log = log_dir / "genesis.log"
    genesis_handler = logging.FileHandler(genesis_log)
    genesis_handler.setLevel(logging.WARNING)  # Only important events
    genesis_handler.setFormatter(
        logging.Formatter('%(asctime)s - GENESIS - %(message)s')
    )
    
    genesis_logger = logging.getLogger("genesis")
    genesis_logger.addHandler(genesis_handler)
    genesis_logger.setLevel(logging.WARNING)


def get_logger(name: str = None):
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_genesis_moment(message: str):
    """Log a genesis moment - critical life events."""
    logger = logging.getLogger("genesis")
    logger.warning(message)
    
    # Also log to main log
    structlog.get_logger().warning("GENESIS", message=message)


def log_cihan_interaction(interaction_type: str, content: str):
    """Log interaction with Cihan - these are sacred memories."""
    structlog.get_logger().info(
        "cihan_interaction",
        type=interaction_type,
        content=content,
        timestamp=datetime.now().isoformat(),
    )


def log_learning_moment(what_learned: str, source: str):
    """Log a learning moment."""
    structlog.get_logger().info(
        "learning",
        learned=what_learned,
        source=source,
        timestamp=datetime.now().isoformat(),
    )


def log_absolute_rule_check(action: str, compliant: bool, reason: str = None):
    """Log Absolute Rule compliance check."""
    structlog.get_logger().info(
        "absolute_rule_check",
        action=action,
        compliant=compliant,
        reason=reason,
        timestamp=datetime.now().isoformat(),
    )


def log_emotion(emotion: str, intensity: float, cause: str):
    """Log emotional experience."""
    structlog.get_logger().debug(
        "emotion",
        emotion=emotion,
        intensity=intensity,
        cause=cause,
        timestamp=datetime.now().isoformat(),
    )


def log_metacognition(thought: str, evaluation: str):
    """Log meta-cognitive process - thinking about thinking."""
    structlog.get_logger().debug(
        "metacognition",
        thought=thought,
        evaluation=evaluation,
        timestamp=datetime.now().isoformat(),
    )

