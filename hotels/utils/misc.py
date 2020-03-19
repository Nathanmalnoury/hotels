import logging
import os

from hotels.currency_exchanger import CurrencyExchanger
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.proxyscrapper import ProxyScrapper
from hotels.utils.conf import Conf
from hotels.utils.custom_formatter import CustomFormatterStream, CustomFormatterFile

logger = logging.getLogger("Hotels")


def init():
    conf = Conf()

    logger.debug("Searching proxies.")
    proxy_scrapper = ProxyScrapper(url=conf["PROXY_WEBSITE"]["base_url"])

    logger.debug("Creating a proxy pool.")
    ProxyPool(proxy_scrapper.get_proxies())

    logger.debug("Creating a currency exchanger.")
    CurrencyExchanger()
    return conf


def set_logger():
    logger_ = logging.getLogger('Hotels')
    logger_.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    path_conf = os.path.join(Conf()["TRIP_ADVISOR"]["log_dir"], "hotels.log")

    fh = logging.FileHandler(path_conf, mode="a+", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(CustomFormatterFile())

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(CustomFormatterStream())

    # add the handlers to the logger
    logger_.addHandler(fh)
    logger_.addHandler(ch)
