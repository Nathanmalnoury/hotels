import logging
import os

from hotels.conf_reader import ConfReader
from hotels.currency_exchanger import CurrencyExchanger
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.proxyscrapper import ProxyScrapper


def init():
    set_logger()
    logger = logging.getLogger("Hotels")
    os.environ["geckodriver"] = "/home/nathan/Projects/hotels/data/"

    conf_reader = ConfReader()
    conf = conf_reader.get("conf.ini")
    logger.info("Searching proxies.")

    proxy_scrapper = ProxyScrapper(url=conf["PROXY_WEBSITE"]["base_url"])
    proxy_scrapper.load_soup(use_proxy=False)
    proxies = proxy_scrapper.get_proxies()

    logger.info("Creating a proxy pool.")
    ProxyPool.initialize(proxies=proxies)

    logger.info("Creating a currency exchanger.")
    CurrencyExchanger.initialize()
    return conf


def set_logger():
    logger = logging.getLogger('Hotels')
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('hotels.log')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter(fmt='%(asctime)s:%(levelname)s: %(module)s/%(funcName)s : %(message)s',
                                  datefmt="%H:%M:%S")
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.debug("logger setup")
