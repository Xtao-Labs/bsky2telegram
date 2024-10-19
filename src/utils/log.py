import logging

from coloredlogs import ColoredFormatter

logs = logging.getLogger("B2T")

logging_format = "%(levelname)s [%(asctime)s] [%(name)s] %(message)s"
logging_handler = logging.StreamHandler()
logging_handler.setFormatter(ColoredFormatter(logging_format))

logging.basicConfig(
    level=logging.INFO,
    handlers=[logging_handler],
)

root_logger = logging.getLogger()
root_logger.setLevel(logging.CRITICAL)

pyro_logger = logging.getLogger("pyrogram")
pyro_logger.setLevel(logging.CRITICAL)

logs.setLevel(logging.INFO)
