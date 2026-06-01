import logging
import os
import sys

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logger = logging.getLogger("taskmanager")
logger.setLevel(getattr(logging, LOG_LEVEL))

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))
logger.addHandler(handler)

logging.getLogger("uvicorn.access").handlers = []
logging.getLogger("uvicorn.access").addHandler(handler)
logging.getLogger("uvicorn.access").setLevel(logging.INFO)
logging.getLogger("uvicorn.error").setLevel(logging.INFO)
