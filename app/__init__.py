import logging
from logging.handlers import RotatingFileHandler

# Logging configuration
log_filename = "tradestation.log"
log_max_size = 1 * 1024 * 1024  # 1 MB

# Create a logger
logger = logging.getLogger("streamer")
logger.setLevel(logging.DEBUG)

# Create a file handler with log rotation
handler = RotatingFileHandler(log_filename, maxBytes=log_max_size, backupCount=5)

# Create a formatter
formatter = logging.Formatter("%(asctime)s [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)
