import logging


def get_logger() -> logging.Logger:
    return logging.getLogger("uvicorn.error")
