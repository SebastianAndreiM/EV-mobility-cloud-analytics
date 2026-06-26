"""Structured logging to console and logs/app.log.

Emits JSON lines. Never logs passwords or raw JWT tokens (callers are
responsible for not passing them; this module also masks an `authorization`
field if present in `extra`).
"""
import json
import logging
import os
import sys
from datetime import datetime, timezone

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

_SENSITIVE_KEYS = {"password", "authorization", "token", "access_token", "jwt"}


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Attach safe extras
        for key, value in getattr(record, "extra_fields", {}).items():
            if key.lower() in _SENSITIVE_KEYS:
                continue
            payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(level: str = "INFO") -> None:
    os.makedirs(LOG_DIR, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    formatter = JsonFormatter()

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    root.addHandler(console)

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)
    root.addHandler(file_handler)

    # quiet noisy libraries
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, level: int, message: str, **fields) -> None:
    """Helper to log with structured extra fields."""
    safe = {k: v for k, v in fields.items() if k.lower() not in _SENSITIVE_KEYS}
    logger.log(level, message, extra={"extra_fields": safe})
