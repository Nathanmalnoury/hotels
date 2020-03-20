"""
Init.

Loads Conf singleton and set up the logger.
"""
import logging

from hotels.utils.conf import Conf
from hotels.utils.misc import set_logger

Conf("conf.ini")
set_logger()
logger = logging.getLogger("Hotels")
