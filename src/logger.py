import inspect
from logging import getLogger, basicConfig, DEBUG  

def logger(*args, level='DEBUG'):
    """Logs the filename, line number, and any arguments at the specified log level.

    Args:
    *args: Any arguments to be logged.
    level: The log level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Defaults to 'DEBUG'.
    """
    caller_frame = inspect.currentframe().f_back
    filename = caller_frame.f_code.co_filename
    lineno = caller_frame.f_lineno
    message = f"File \"{filename}\", line {lineno}: {' '.join(map(str, args))}"

    logger = getLogger(__name__)
    color_map = {
        'DEBUG': '\033[94m',              # Blue
        'INFO': '\033[38;2;51;204;153m',  # Light greenish-blue color (#33CC99)
        'WARNING': '\033[93m',            # Yellow
        'ERROR': '\033[91m',              # Red
        'CRITICAL': '\033[95m'            # Purple
    }
    reset_color = '\033[0m'
    colored_message = f"{color_map.get(level, '')}{message}{reset_color}"

    if level == 'DEBUG':
        logger.debug(colored_message)
    elif level == 'INFO':
        logger.info(colored_message)
    elif level == 'WARNING':
        logger.warning(colored_message)
    elif level == 'ERROR':
        logger.error(colored_message)
    elif level == 'CRITICAL':
        logger.critical(colored_message)
    else:
        raise ValueError(f"Invalid log level: {level}")

    # Logging configuration
    basicConfig(
        level=DEBUG, 
        format='%(asctime)s - %(levelname)s - %(message)s',
    )