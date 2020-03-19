import logging

from hotels.utils.conf import Conf
from hotels.utils.misc import set_logger

Conf("conf.ini")
set_logger()
logger = logging.getLogger("Hotels")
logger.debug("initialized logger and conf")
