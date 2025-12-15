import logging
import sys
from typing import Optional
from colorlog import ColoredFormatter


class ContextFormatter(ColoredFormatter):
    """Пользовательский форматтер логов."""

    def format(self, record: logging.LogRecord) -> str:  # noqa
        """Форматирует данные logging."""
        formatted_message: str = super().format(record=record)
        default_log_record = logging.LogRecord("", 0, "", 0, None, None, None, None, None)
        context_message = "Context: "
        for key, value in record.__dict__.items():
            if key not in (default_log_record.__dict__) and key not in (
                "message",
                "asctime",
            ):
                context_message += f"({key}={value})| "
        if context_message != "Context: ":
            formatted_message = formatted_message + " " + context_message
        return formatted_message


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Logging settings
    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    Returns:
        configured logger
    """
    logger = logging.getLogger("retailcrm_crud_app")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    logger.handlers.clear()

    formatter = ContextFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get logger with entered name.
    Args:
        name:  logger name (if None, returns root logger)
    Returns:
        Logger
    """
    if name:
        return logging.getLogger(f"retailcrm_crud_app.{name}")
    return logging.getLogger("retailcrm_crud_app")
