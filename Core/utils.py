import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handle_error(error_message, exception=None):
    logger.error(error_message)
    if exception:
        logger.error(f"Exception: {exception}")
    raise Exception(error_message)