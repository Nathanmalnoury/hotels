import logging


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;1m"
    yellow = "\x1b[33;1m"
    red = "\x1b[31;1m"
    blue = "\x1b[34;1m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = '%(asctime)s:%(levelname)s:%(filename)s-l%(lineno)d: %(message)s'
    datefmt = "%H:%M:%S"

    FORMATS = {
        logging.DEBUG: blue + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)