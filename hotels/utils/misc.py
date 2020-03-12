import logging
import os

from hotels.currency_exchanger import CurrencyExchanger
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.proxyscrapper import ProxyScrapper
from hotels.utils.conf_reader import ConfReader
from hotels.utils.custom_formatter import CustomFormatter


def init():
    set_logger()
    logger = logging.getLogger("Hotels")
    conf = ConfReader.get("conf.ini")

    logger.info("Searching proxies.")
    proxy_scrapper = ProxyScrapper(url=conf["PROXY_WEBSITE"]["base_url"])

    logger.info("Creating a proxy pool.")
    ProxyPool.initialize(proxies=proxy_scrapper.get_proxies())

    logger.info("Creating a currency exchanger.")
    CurrencyExchanger.initialize()
    return conf


def set_logger():
    logger = logging.getLogger('Hotels')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    conf = ConfReader.get("conf.ini")

    path_conf = os.path.join(conf["TRIP_ADVISOR"]["log_dir"], "hotels.log")
    fh = logging.FileHandler(path_conf, mode="a+")
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    fh.setFormatter(CustomFormatter())
    ch.setFormatter(CustomFormatter())
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.debug("logger setup")
