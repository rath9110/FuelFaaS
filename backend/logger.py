import logging
import sys
import json
from datetime import datetime
from typing import Any
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_data"):
            log_data["extra"] = record.extra_data
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Colored text formatter for development."""
    
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        record.levelname = f"{color}{record.levelname}{reset}"
        return super().format(record)


def setup_logger(
    name: str = "fuelguard",
    level: str = "INFO",
    log_format: str = "text",
    log_file: str | None = None
) -> logging.Logger:
    """
    Set up application logger with configurable format and output.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Format type ('json' or 'text')
        log_file: Optional file path for logging to file
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if log_format == "json":
        console_handler.setFormatter(JSONFormatter())
    else:
        text_format = (
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s"
        )
        console_handler.setFormatter(TextFormatter(text_format))
    
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(JSONFormatter())  # Always use JSON for files
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "fuelguard") -> logging.Logger:
    """Get or create a logger instance."""
    return logging.getLogger(name)


# Example usage with extra context
class LoggerAdapter(logging.LoggerAdapter):
    """Adapter to add contextual information to log records."""
    
    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        if hasattr(self, "extra") and self.extra:
            kwargs["extra"]["extra_data"] = self.extra
        
        return msg, kwargs
