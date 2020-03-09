import logging
import os

import pandas as pd

from hotels.conf_reader import ConfReader
from hotels.currency_exchanger import CurrencyExchanger
from hotels.models.hotel import Hotel
from hotels.proxy_pool import ProxyPool
from hotels.scrappers.proxyscrapper import ProxyScrapper


def save_as_excel(list_of_hotels, path_to_file):
    logger = logging.getLogger("Hotels")
    list_of_dicts = [hotel.__dict__ for hotel in list_of_hotels]
    df = pd.DataFrame(list_of_dicts)
    df.to_excel(path_to_file)
    logger.debug("Excel written")


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


def excel_to_hotels(path):
    df = pd.read_excel(path, index_col=0)
    list_hotels = []
    for i, data in df.iterrows():
        name = data["name"] if not pd.isna(data["name"]) else None
        rating = data["rating"] if not pd.isna(data["rating"]) else None
        price = data["price"] if not pd.isna(data["price"]) else None
        currency = data["currency"] if not pd.isna(data["currency"]) else None
        detail_url = data["detail_url"] if not pd.isna(data["detail_url"]) else None

        list_hotels.append(
            Hotel(
                name=name,
                rating=rating,
                price=price,
                currency=currency,
                detail_url=detail_url,
                needs_root=False,
            )
        )
    return list_hotels


def get_incomplete_hotel(list_hotels):
    incomplete = []
    for hotel in list_hotels:
        if not hotel.is_complete:
            incomplete.append(hotel)
    return incomplete


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
